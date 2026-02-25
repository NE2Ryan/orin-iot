import serial
import time

PORT = '/dev/ttyTHS1'
BAUDS = [9600, 38400, 115200, 4800, 57600]

def scan():
    for baud in BAUDS:
        print(f"Testing {baud} baud...")
        try:
            ser = serial.Serial(PORT, baud, timeout=2)
            time.sleep(1)
            # Read a larger chunk to be sure
            data = ser.read(1024)
            ser.close()
            
            # Look for common NMEA headers
            headers = [b'GNGGA', b'GPGGA', b'GNRMC', b'GPRMC', b'GNZDA']
            found = False
            for h in headers:
                if h in data:
                    print(f"!!! SUCCESS: Found {h.decode()} at {baud} baud !!!")
                    found = True
                    break
            
            if not found:
                print(f"  No valid NMEA headers found at {baud}.")
                if len(data) > 0:
                    print(f"  (Received {len(data)} bytes of junk/noise)")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    scan()
