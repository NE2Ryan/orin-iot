import serial
import serial.tools.list_ports
import sys

def find_gnss_port():
    """Finds common USB serial port names on Mac."""
    ports = list(serial.tools.list_ports.comports())
    # Common patterns for USB serial on Mac
    patterns = ['usbserial', 'usbmodem', 'cp210x', 'ch340']
    
    for port in ports:
        if any(p in port.device.lower() for p in patterns):
            return port.device
    return None

def main():
    port = find_gnss_port()
    
    if not port:
        print("Could not find a USB GNSS module automatically.")
        print("Available ports:")
        for p in serial.tools.list_ports.comports():
            print(f" - {p.device}")
        port = input("Please enter your port manually (e.g., /dev/cu.usbserial-10): ")
    
    baud_rate = 9600  # Default for most GNSS modules
    
    print(f"Connecting to {port} at {baud_rate} baud...")
    
    try:
        with serial.Serial(port, baud_rate, timeout=1) as ser:
            print("Connected! Waiting for GNSS data (NMEA)...")
            print("Press Ctrl+C to stop.")
            
            while True:
                line = ser.readline().decode('ascii', errors='replace').strip()
                if line:
                    print(line)
                    
    except serial.SerialException as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Stopping...")

if __name__ == "__main__":
    main()
