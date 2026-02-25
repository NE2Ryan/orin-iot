from machine import Pin, UART
import time

# Pins
RX_PIN = 26
TX_PIN = 25
BAUD_RATES = [9600, 4800, 115200]

def test_gnss(baud):
    print("\n--- Testing Baud Rate: {} ---".format(baud))
    # Initialize UART 2
    uart = UART(2)
    # Use positional arguments or init to avoid keyword argument error
    uart.init(baud, bits=8, parity=None, stop=1, rx=RX_PIN, tx=TX_PIN)
    
    start = time.time()
    while time.time() - start < 5:
        if uart.any():
            data = uart.read()
            if data:
                try:
                    print(data.decode('ascii', 'replace'), end='')
                except:
                    print(data, end='')
        time.sleep(0.1)

def main():
    print("GNSS RAW DEBUGGER (Compatible Version)")
    print("Wiring: GNSS TX -> GPIO 26, GNSS RX -> GPIO 25")
    
    for b in BAUD_RATES:
        test_gnss(b)
        
    print("\n\nDebug complete.")
    print("If NO text appeared, swap wires on pins 25 and 26.")

if __name__ == "__main__":
    main()
