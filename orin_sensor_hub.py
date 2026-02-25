#!/usr/bin/env python3
"""
Jetson Orin Nano — Direct Sensor Hub
Reads GNSS (UART) + MPU6500 (I2C) + AK8963 Magnetometer (I2C)
and displays live tilt-compensated compass heading + GPS data.

Usage:
    sudo python3 orin_sensor_hub.py
    sudo python3 orin_sensor_hub.py --i2c-bus 7 --uart /dev/ttyTHS1
"""

import argparse
import json
import math
import os
import signal
import sys
import time

try:
    import smbus2
except ImportError:
    sys.exit("Missing dependency: pip3 install smbus2")

try:
    import serial
except ImportError:
    sys.exit("Missing dependency: pip3 install pyserial")


# ── Sensor Addresses ────────────────────────────────────────────────
MPU6500_ADDR = 0x68
AK8963_ADDR  = 0x0C

# ── MPU6500 Registers ───────────────────────────────────────────────
MPU_PWR_MGMT_1   = 0x6B
MPU_INT_PIN_CFG  = 0x37
MPU_ACCEL_XOUT_H = 0x3B
MPU_GYRO_XOUT_H  = 0x43

# ── AK8963 Registers ────────────────────────────────────────────────
AK_CNTL1 = 0x0A
AK_ST1   = 0x02
AK_HXL   = 0x03
AK_ST2   = 0x09

# ── Magnetometer Calibration (from your ESP32 config) ───────────────
MAG_BIAS  = (35.325, 66.525, 17.100)
MAG_SCALE = (1.029, 1.025, 0.950)
DECLINATION = 0.0


class MPU6500:
    """MPU6500 IMU driver using Linux smbus2."""

    def __init__(self, bus, address=MPU6500_ADDR):
        self.bus = bus
        self.addr = address
        self._init()

    def _init(self):
        # Wake up (clear sleep bit)
        self.bus.write_byte_data(self.addr, MPU_PWR_MGMT_1, 0x00)
        time.sleep(0.01)
        # Enable I2C bypass so the host can talk to the AK8963 directly
        self.bus.write_byte_data(self.addr, MPU_INT_PIN_CFG, 0x02)
        time.sleep(0.01)

    def _read_word(self, reg):
        h = self.bus.read_byte_data(self.addr, reg)
        l = self.bus.read_byte_data(self.addr, reg + 1)
        val = (h << 8) | l
        return val - 65536 if val > 32767 else val

    @property
    def acceleration(self):
        """(x, y, z) in Gs  (±2 g range, 16384 LSB/g)."""
        ax = self._read_word(MPU_ACCEL_XOUT_H)
        ay = self._read_word(MPU_ACCEL_XOUT_H + 2)
        az = self._read_word(MPU_ACCEL_XOUT_H + 4)
        return (ax / 16384.0, ay / 16384.0, az / 16384.0)

    @property
    def gyro(self):
        """(x, y, z) in deg/s  (±250 dps range, 131 LSB/dps)."""
        gx = self._read_word(MPU_GYRO_XOUT_H)
        gy = self._read_word(MPU_GYRO_XOUT_H + 2)
        gz = self._read_word(MPU_GYRO_XOUT_H + 4)
        return (gx / 131.0, gy / 131.0, gz / 131.0)


class AK8963:
    """AK8963 magnetometer driver using Linux smbus2."""

    def __init__(self, bus, address=AK8963_ADDR):
        self.bus = bus
        self.addr = address
        self._init()

    def _init(self):
        # Power-down
        self.bus.write_byte_data(self.addr, AK_CNTL1, 0x00)
        time.sleep(0.01)
        # Continuous measurement mode 2, 16-bit output
        self.bus.write_byte_data(self.addr, AK_CNTL1, 0x16)
        time.sleep(0.01)

    def _read_word_le(self, reg):
        """Read little-endian signed 16-bit word (AK8963 byte order)."""
        l = self.bus.read_byte_data(self.addr, reg)
        h = self.bus.read_byte_data(self.addr, reg + 1)
        val = (h << 8) | l
        return val - 65536 if val > 32767 else val

    @property
    def magnetic(self):
        """(x, y, z) in µT  (0.15 µT/LSB).  Returns None if data not ready."""
        st1 = self.bus.read_byte_data(self.addr, AK_ST1)
        if not (st1 & 0x01):
            return None

        mx = self._read_word_le(AK_HXL)
        my = self._read_word_le(AK_HXL + 2)
        mz = self._read_word_le(AK_HXL + 4)

        # Must read ST2 to signal measurement complete
        self.bus.read_byte_data(self.addr, AK_ST2)

        scale = 0.15
        return (mx * scale, my * scale, mz * scale)


# ── GNSS Parser ─────────────────────────────────────────────────────

class GNSSReader:
    """Reads NMEA from a serial UART and maintains latest fix."""

    def __init__(self, port, baud=9600):
        self.ser = serial.Serial(port, baud, timeout=0.1)
        self.data = {"lat": 0.0, "lon": 0.0, "alt": 0.0, "sats": 0, "fix": False}

    def _parse_coord(self, value, direction):
        if not value or not direction:
            return 0.0
        try:
            dot = value.index('.')
            dd = int(value[:dot - 2])
            mm = float(value[dot - 2:])
            result = dd + mm / 60.0
            return -result if direction in ('S', 'W') else result
        except (ValueError, IndexError):
            return 0.0

    def update(self):
        """Call frequently — reads available NMEA sentences and updates fix."""
        while self.ser.in_waiting:
            try:
                line = self.ser.readline().decode('ascii', errors='ignore').strip()
            except Exception:
                continue

            if not (line.startswith('$GNGGA') or line.startswith('$GPGGA')):
                continue

            parts = line.split(',')
            try:
                self.data["sats"] = int(parts[7]) if parts[7] else 0
                if parts[6] != '0':
                    self.data["lat"] = self._parse_coord(parts[2], parts[3])
                    self.data["lon"] = self._parse_coord(parts[4], parts[5])
                    self.data["alt"] = float(parts[9]) if parts[9] else 0.0
                    self.data["fix"] = True
                else:
                    self.data["fix"] = False
            except (IndexError, ValueError):
                pass

    def close(self):
        self.ser.close()


# ── Heading Calculation ──────────────────────────────────────────────

def compute_heading(acc, mag_raw):
    """Tilt-compensated compass heading (degrees 0-360)."""
    ax, ay, az = acc

    roll  = math.atan2(ay, az)
    pitch = math.atan2(-ax, math.sqrt(ay * ay + az * az))

    mx = (mag_raw[0] - MAG_BIAS[0]) * MAG_SCALE[0]
    my = (mag_raw[1] - MAG_BIAS[1]) * MAG_SCALE[1]
    mz = (mag_raw[2] - MAG_BIAS[2]) * MAG_SCALE[2]

    mx_h = mx * math.cos(pitch) + mz * math.sin(pitch)
    my_h = (mx * math.sin(roll) * math.sin(pitch)
            + my * math.cos(roll)
            - mz * math.sin(roll) * math.cos(pitch))

    heading = (math.degrees(math.atan2(mx_h, my_h)) + DECLINATION) % 360
    return heading, math.degrees(pitch), math.degrees(roll)


# ── Auto-detect I2C bus ──────────────────────────────────────────────

def find_i2c_bus():
    """Try common Orin I2C buses and return the first one with MPU6500."""
    candidates = [1, 7, 0, 2, 8]
    for bus_num in candidates:
        dev = f"/dev/i2c-{bus_num}"
        if not os.path.exists(dev):
            continue
        try:
            bus = smbus2.SMBus(bus_num)
            bus.read_byte_data(MPU6500_ADDR, MPU_PWR_MGMT_1)
            bus.close()
            return bus_num
        except Exception:
            try:
                bus.close()
            except Exception:
                pass
    return None


# ── Main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Orin Nano Sensor Hub")
    parser.add_argument("--i2c-bus", type=int, default=None,
                        help="I2C bus number (auto-detected if omitted)")
    parser.add_argument("--uart", default="/dev/ttyTHS1",
                        help="GNSS UART device (default: /dev/ttyTHS1)")
    parser.add_argument("--baud", type=int, default=9600,
                        help="GNSS baud rate (default: 9600)")
    parser.add_argument("--hz", type=float, default=10,
                        help="Output rate in Hz (default: 10)")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON instead of formatted text")
    args = parser.parse_args()

    # ── I2C ──
    bus_num = args.i2c_bus
    if bus_num is None:
        print("Auto-detecting I2C bus...", end=" ", flush=True)
        bus_num = find_i2c_bus()
        if bus_num is None:
            sys.exit("No I2C bus found with MPU6500. "
                     "Make sure I2C is enabled (sudo jetson-io.py) "
                     "and the sensor is wired correctly.")
        print(f"found on /dev/i2c-{bus_num}")

    bus = smbus2.SMBus(bus_num)
    imu = MPU6500(bus)
    mag = AK8963(bus)
    print(f"IMU + Magnetometer initialised on /dev/i2c-{bus_num}")

    # ── GNSS ──
    gps = GNSSReader(args.uart, args.baud)
    print(f"GNSS listening on {args.uart} @ {args.baud} baud")

    print("─" * 60)
    print("Press Ctrl+C to stop.\n")

    interval = 1.0 / args.hz

    def shutdown(sig, frame):
        print("\nShutting down...")
        gps.close()
        bus.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    while True:
        t0 = time.monotonic()

        # Update GNSS
        gps.update()

        # Read sensors
        acc = imu.acceleration
        m = mag.magnetic

        if m:
            heading, pitch, roll = compute_heading(acc, m)
        else:
            heading, pitch, roll = 0.0, 0.0, 0.0
            pitch = math.degrees(math.atan2(-acc[0], math.sqrt(acc[1]**2 + acc[2]**2)))
            roll  = math.degrees(math.atan2(acc[1], acc[2]))

        g = gps.data

        if args.json:
            out = {
                "heading": round(heading, 2),
                "pitch":   round(pitch, 2),
                "roll":    round(roll, 2),
                "lat":     g["lat"],
                "lon":     g["lon"],
                "alt":     g["alt"],
                "fix":     g["fix"],
                "sats":    g["sats"],
            }
            print(json.dumps(out), flush=True)
        else:
            fix_str = f"YES ({g['sats']} sats)" if g["fix"] else f"NO  ({g['sats']} sats)"
            print(
                f"\rHeading: {heading:6.1f}°  |  "
                f"Pitch: {pitch:+6.1f}°  |  "
                f"Roll: {roll:+6.1f}°  |  "
                f"Fix: {fix_str}  |  "
                f"Lat: {g['lat']:11.6f}  Lon: {g['lon']:12.6f}  Alt: {g['alt']:.1f}m",
                end="", flush=True,
            )

        elapsed = time.monotonic() - t0
        remaining = interval - elapsed
        if remaining > 0:
            time.sleep(remaining)


if __name__ == "__main__":
    main()
