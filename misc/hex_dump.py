import serial
import sys

PORT = '/dev/ttyTHS1'
BAUD = 9600

def main():
    print(f"Opening {PORT} at {BAUD} for Hex Dump...")
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        while True:
            data = ser.read(16)
            if data:
                # Print hex representation and ASCII attempt
                hex_str = ' '.join([f'{b:02x}' for b in data])
                ascii_str = ''.join([chr(b) if 32 <= b <= 126 else '.' for b in data])
                print(f"{hex_str}  |{ascii_str}|")
    except KeyboardInterrupt:
        print("Stopping...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals():
            ser.close()

if __name__ == "__main__":
    main()
