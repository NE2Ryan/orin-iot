from machine import Pin, I2C, UART
import ssd1306
import mpu6500
import ak8963
import time
import math

# --- Configuration ---
# I2C for OLED and IMU
I2C_SDA = 4
I2C_SCL = 5
# UART for GNSS
UART_ID = 2
RX_PIN = 26
TX_PIN = 25
BAUD = 9600

# --- Initialization ---
print("Initializing System...")
i2c = I2C(1, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL))
gnss_serial = UART(UART_ID, baudrate=BAUD, rx=RX_PIN, tx=TX_PIN, timeout=100)

# 1. Initialize OLED
try:
    oled = ssd1306.SSD1306_I2C(128, 64, i2c)
    print("OLED Ready")
except:
    oled = None

# 2. Initialize MPU6500 & AK8963 (Mag)
# The MPU6500 driver handles the bypass to make Mag visible at 0x0C
try:
    imu = mpu6500.MPU6500(i2c, address=0x68)
    mag = ak8963.AK8963(i2c, address=0x0C)
    print("IMU & Mag Ready")
except Exception as e:
    print(f"IMU/Mag Error: {e}")
    imu = None
    mag = None

# --- GNSS State ---
gnss_data = {
    "lat": 0.0,
    "lon": 0.0,
    "sats": "0",
    "fix": False
}

def parse_nmea_coord(value, direction):
    if not value or not direction: return None
    try:
        dot_idx = value.find('.')
        dd = int(value[:dot_idx-2])
        mm = float(value[dot_idx-2:])
        decimal = dd + (mm / 60)
        if direction in ['S', 'W']: decimal = -decimal
        return decimal
    except: return None

def check_gnss():
    if gnss_serial.any():
        line = gnss_serial.readline()
        try:
            msg = line.decode('ascii').strip()
            if msg.startswith('$GNGGA') or msg.startswith('$GPGGA'):
                parts = msg.split(',')
                if len(parts) >= 10:
                    gnss_data["sats"] = parts[7]
                    if parts[6] != '0': # Fix quality
                        gnss_data["lat"] = parse_nmea_coord(parts[2], parts[3])
                        gnss_data["lon"] = parse_nmea_coord(parts[4], parts[5])
                        gnss_data["fix"] = True
                    else:
                        gnss_data["fix"] = False
        except:
            pass

def draw_dashboard(heading, accel):
    if not oled: return
    oled.fill(0)
    
    # --- Compass (Left) ---
    cx, cy, r = 32, 32, 20
    oled.draw_circle(cx, cy, r) if hasattr(oled, 'draw_circle') else oled.rect(cx-r, cy-r, r*2, r*2, 1)
    
    rad = math.radians(-heading)
    nx = int(cx + r * math.sin(rad))
    ny = int(cy - r * math.cos(rad))
    oled.line(cx, cy, nx, ny, 1)
    oled.text(f"H:{int(heading)}", 0, 0)

    # --- GNSS Info (Right Top) ---
    oled.text("GNSS:", 68, 0)
    if gnss_data["fix"]:
        oled.text(f"LA:{gnss_data['lat']:.3f}", 68, 12)
        oled.text(f"LO:{gnss_data['lon']:.3f}", 68, 22)
    else:
        oled.text("No Fix", 68, 12)
    oled.text(f"Sats:{gnss_data['sats']}", 68, 32)

    # --- Leveler (Right Bottom) ---
    rx, ry, rw, rh = 70, 45, 50, 15
    oled.rect(rx, ry, rw, rh, 1)
    # Simple horizontal leveler using Y accel
    ax, ay, az = accel
    bubble_x = int(rx + (rw/2) + (ay * (rw/2)))
    bubble_x = max(rx+2, min(rx+rw-4, bubble_x))
    oled.fill_rect(bubble_x, ry+2, 4, rh-4, 1)
    
    oled.show()

def main():
    print("Running Dashboard...")
    while True:
        check_gnss()
        
        # Read IMU
        accel = imu.acceleration if imu else (0,0,0)
        m_data = mag.magnetic if mag else None
        
        heading = 0
        if m_data:
            mx, my, mz = m_data
            heading = math.degrees(math.atan2(my, mx))
            if heading < 0: heading += 360
        
        draw_dashboard(heading, accel)
        time.sleep(0.1)

if __name__ == "__main__":
    main()
