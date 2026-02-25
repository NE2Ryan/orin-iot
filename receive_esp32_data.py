import serial
import json
import time
import sys

def find_esp32_port():
    """Attempt to find the ESP32 serial port."""
    ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', '/dev/ttyACM1']
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            return port
        except (OSError, serial.SerialException):
            continue
    return None

def main():
    port = find_esp32_port()
    if not port:
        print("Error: Could not find ESP32. Check USB connection.")
        sys.exit(1)

    print(f"Connecting to ESP32 on {port}...")
    
    try:
        # MicroPython default baud rate is 115200
        ser = serial.Serial(port, 115200, timeout=1)
        time.sleep(2)  # Wait for connection to stabilize
        
        print("Receiving data (Press Ctrl+C to stop)...")
        print("-" * 60)
        
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    try:
                        data = json.loads(line)
                        
                        # Format the output for readability
                        out = (
                            f"Heading: {data['heading']:>6}° | "
                            f"Pitch: {data['pitch']:>6}° | "
                            f"Roll: {data['roll']:>6}° | "
                            f"Fix: {'YES' if data['fix'] else 'NO'} ({data['sats']} sats)\n"
                            f"Lat: {data['lat']:.6f} | Lon: {data['lon']:.6f} | Alt: {data['alt']:.1f}m"
                        )
                        
                        # Clear line and print (simple refresh effect)
                        sys.stdout.write("\033[K" + out + "\033[F")
                        sys.stdout.flush()
                        
                    except json.JSONDecodeError:
                        # Ignore non-JSON lines (like boot messages or REPL prompts)
                        continue
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        if 'ser' in locals():
            ser.close()

if __name__ == "__main__":
    main()
