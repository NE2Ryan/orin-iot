import serial
import time
import sys
import os

# --- Configuration ---
SERIAL_PORT = '/dev/ttyTHS1' 
BAUD_RATE = 9600
TIMEOUT = 1

class GNSSState:
    def __init__(self):
        self.lat = 0.0
        self.lon = 0.0
        self.sats = 0
        self.fix_quality = 0
        self.speed_knots = 0.0
        self.last_update = "N/A"

def parse_nmea_coord(value, direction):
    """Converts NMEA DDMM.MMMM to decimal degrees."""
    if not value or not direction:
        return 0.0
    try:
        dot_idx = value.find('.')
        dd = int(value[:dot_idx-2])
        mm = float(value[dot_idx-2:])
        decimal = dd + (mm / 60)
        if direction in ['S', 'W']:
            decimal = -decimal
        return decimal
    except:
        return 0.0

def update_dashboard(state):
    """Prints a non-scrolling dashboard to the terminal."""
    # Clear screen and move cursor to top-left
    sys.stdout.write("\033[H\033[J")
    
    status = "FIXED" if state.fix_quality > 0 else "WAITING"
    color = "\033[92m" if state.fix_quality > 0 else "\033[93m"
    reset = "\033[0m"

    print("="*40)
    print(f" JETSON ORIN GNSS MONITOR ({SERIAL_PORT})")
    print("="*40)
    print(f" Status:    {color}{status}{reset}")
    print(f" Satellites: {state.sats}")
    print(f" Latitude:  {state.lat:.6f}")
    print(f" Longitude: {state.lon:.6f}")
    print(f" Speed:     {state.speed_knots * 1.852:.2f} km/h")
    print(f" Last Sync: {state.last_update}")
    print("="*40)
    print(" Press Ctrl+C to exit")

def main():
    state = GNSSState()
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
    except Exception as e:
        print(f"Error: Could not open {SERIAL_PORT}: {e}")
        return

    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('ascii', errors='replace').strip()
                
                if line.startswith('$'):
                    parts = line.split(',')
                    header = parts[0]
                    
                    # GGA: Fix data, Satellites
                    if header in ['$GPGGA', '$GNGGA'] and len(parts) >= 10:
                        state.fix_quality = int(parts[6]) if parts[6] else 0
                        state.sats = int(parts[7]) if parts[7] else 0
                        if state.fix_quality > 0:
                            state.lat = parse_nmea_coord(parts[2], parts[3])
                            state.lon = parse_nmea_coord(parts[4], parts[5])
                            state.last_update = time.strftime("%H:%M:%S")

                    # RMC: Speed, Coordinates
                    elif header in ['$GPRMC', '$GNRMC'] and len(parts) >= 9:
                        if parts[2] == 'A': # 'A' = Valid, 'V' = Warning
                            state.speed_knots = float(parts[7]) if parts[7] else 0.0
                            state.lat = parse_nmea_coord(parts[3], parts[4])
                            state.lon = parse_nmea_coord(parts[5], parts[6])
                            state.last_update = time.strftime("%H:%M:%S")

                update_dashboard(state)
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping GNSS monitor...")
    finally:
        ser.close()

if __name__ == "__main__":
    main()
