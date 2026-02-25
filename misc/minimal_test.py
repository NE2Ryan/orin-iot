import serial
import sys

PORT = '/dev/ttyTHS1'
BAUD = 4800

def main():
    print(f"Opening {PORT} at {BAUD}...")
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        while True:
            # Read one byte at a time to see exactly what's coming
            char = ser.read(1)
            if char:
                # Print the character directly to stdout
                sys.stdout.write(char.decode('ascii', errors='replace'))
                sys.stdout.flush()
    except KeyboardInterrupt:
        print("
Stopping...")
    finally:
        if 'ser' in locals():
            ser.close()

if __name__ == "__main__":
    main()
