import serial
import time

PORT = '/dev/ttyTHS1'
BAUDS = [4800, 9600, 19200, 38400, 57600, 115200]

def scan():
    for baud in BAUDS:
        print(f"Testing {baud} baud...")
        try:
            ser = serial.Serial(PORT, baud, timeout=1)
            # Read a chunk of data
            time.sleep(0.5)
            data = ser.read(256)
            ser.close()
            
            if b'$' in data:
                print(f"!!! SUCCESS: Found NMEA data at {baud} baud !!!")
                # Try to print a decoded line
                try:
                    start_idx = data.find(b'$')
                    end_idx = data.find(b'', start_idx)
                    if end_idx > start_idx:
                        print(f"Sample: {data[start_idx:end_idx].decode('ascii', errors='replace')}")
                except:
                    pass
                return
            else:
                print(f"  No NMEA start character ($) found at {baud}.")
        except Exception as e:
            print(f"  Error opening port at {baud}: {e}")

if __name__ == "__main__":
    scan()
