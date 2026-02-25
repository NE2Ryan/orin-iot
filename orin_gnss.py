import serial
import time
import sys

# --- Configuration ---
# Update this port based on your dmesg output (usually /dev/ttyUSB0 or /dev/ttyACM0)
SERIAL_PORT = '/dev/ttyUSB0' 
BAUD_RATE = 9600
TIMEOUT = 1

def parse_nmea_coord(value, direction):
    """Converts NMEA DDMM.MMMM to decimal degrees."""
    if not value or not direction:
        return None
    try:
        # Latitude is DDMM.MMMM (2 digits for deg)
        # Longitude is DDDMM.MMMM (3 digits for deg)
        dot_idx = value.find('.')
        if dot_idx < 0:
            return None
            
        dd = int(value[:dot_idx-2])
        mm = float(value[dot_idx-2:])
        decimal = dd + (mm / 60)
        if direction in ['S', 'W']:
            decimal = -decimal
        return decimal
    except Exception:
        return None

def main():
    print(f"Connecting to GNSS on {SERIAL_PORT} at {BAUD_RATE} baud...")
    
    try:
        # Initialize Serial
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
    except serial.SerialException as e:
        print(f"Error: Could not open serial port {SERIAL_PORT}: {e}")
        print("Hint: Check if the device is plugged in or try /dev/ttyACM0")
        sys.exit(1)

    print("Waiting for GNSS data... (Press Ctrl+C to stop)")
    
    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline()
                try:
                    # Decode bytes to string
                    decoded_line = line.decode('ascii', errors='replace').strip()
                    
                    if decoded_line.startswith('$'):
                        parts = decoded_line.split(',')
                        
                        # Look for $GPGGA or $GNGGA for position data
                        if parts[0] in ['$GPGGA', '$GNGGA'] and len(parts) >= 10:
                            lat_raw = parts[2]
                            lat_dir = parts[3]
                            lon_raw = parts[4]
                            lon_dir = parts[5]
                            fix_quality = parts[6]
                            sats = parts[7]
                            
                            if fix_quality != '0':  # '0' means no fix
                                lat = parse_nmea_coord(lat_raw, lat_dir)
                                lon = parse_nmea_coord(lon_raw, lon_dir)
                                if lat is not None and lon is not None:
                                    print(f"[{parts[0]}] FIX: Lat {lat:.6f}, Lon {lon:.6f}, Sats {sats}")
                            else:
                                print(f"[{parts[0]}] WAITING: No Fix (Sats: {sats})")
                                
                except Exception as e:
                    # Ignore occasional decoding errors
                    pass
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("
Stopping GNSS monitor...")
    finally:
        ser.close()

if __name__ == "__main__":
    main()
