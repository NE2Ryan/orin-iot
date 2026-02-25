import serial
import time
import sys
from collections import deque

# --- Configuration ---
SERIAL_PORT = '/dev/ttyTHS1' 
BAUD_RATE = 9600
TIMEOUT = 0.1  # Low timeout for responsive character reading

class GNSSState:
    def __init__(self):
        self.lat = 0.0
        self.lon = 0.0
        self.sats = 0
        self.fix_quality = 0
        self.speed_knots = 0.0
        self.last_update = "N/A"
        self.raw_lines = deque(maxlen=10)
        self.total_chars = 0
        self.last_char_time = time.time()

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
    print(f" Bytes In:  {state.total_chars}")
    print("="*40)
    print(" RECENT RAW DATA:")
    for r_line in state.raw_lines:
        print(f" {r_line}")
    print("="*40)
    print(" Press Ctrl+C to exit")

def main():
    state = GNSSState()
    buffer = ""
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
    except Exception as e:
        print(f"Error: Could not open {SERIAL_PORT}: {e}")
        return

    try:
        while True:
            # Read character by character to avoid buffer split issues
            if ser.in_waiting > 0:
                char_bytes = ser.read(1)
                if char_bytes:
                    state.total_chars += 1
                    try:
                        char = char_bytes.decode('ascii', errors='replace')
                        if char == '\n' or char == '\r':
                            if buffer.strip().startswith('$'):
                                line = buffer.strip()
                                state.raw_lines.append(line)
                                
                                parts = line.split(',')
                                header = parts[0]
                                
                                if header in ['$GPGGA', '$GNGGA'] and len(parts) >= 10:
                                    state.fix_quality = int(parts[6]) if parts[6] and parts[6].isdigit() else 0
                                    state.sats = int(parts[7]) if parts[7] and parts[7].isdigit() else 0
                                    if state.fix_quality > 0:
                                        state.lat = parse_nmea_coord(parts[2], parts[3])
                                        state.lon = parse_nmea_coord(parts[4], parts[5])
                                        state.last_update = time.strftime("%H:%M:%S")

                                elif header in ['$GPRMC', '$GNRMC'] and len(parts) >= 9:
                                    if parts[2] == 'A':
                                        state.speed_knots = float(parts[7]) if parts[7] else 0.0
                                        state.lat = parse_nmea_coord(parts[3], parts[4])
                                        state.lon = parse_nmea_coord(parts[5], parts[6])
                                        state.last_update = time.strftime("%H:%M:%S")
                            
                            buffer = "" # Reset buffer for next line
                        else:
                            buffer += char
                    except:
                        pass # Ignore decoding noise

            # Throttle UI update to ~10Hz
            if time.time() - state.last_char_time > 0.1:
                update_dashboard(state)
                state.last_char_time = time.time()
            
    except KeyboardInterrupt:
        print("\nStopping GNSS monitor...")
    finally:
        ser.close()

if __name__ == "__main__":
    main()
