import serial
import time

PORT = '/dev/ttyTHS1'
BAUD = 9600

def main():
    print(f"Starting Loopback Test on {PORT}...")
    print("Ensure Pin 8 and Pin 10 are connected with a jumper wire!")
    
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        test_message = "HELLO_ORIN_UART"
        
        # Clear buffers
        ser.flushInput()
        ser.flushOutput()
        
        # Send message
        print(f"Sending: {test_message}")
        ser.write(test_message.encode())
        
        # Wait a moment
        time.sleep(0.1)
        
        # Read back
        response = ser.read(len(test_message)).decode()
        
        if response == test_message:
            print("!!! SUCCESS: Loopback confirmed! The Orin UART is working perfectly. !!!")
        else:
            print(f"FAILED: Sent '{test_message}', but received '{response}'")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals():
            ser.close()

if __name__ == "__main__":
    main()
