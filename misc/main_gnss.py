from machine import Pin, I2C, UART
import ssd1306
import time

# --- Configuration ---
# OLED I2C pins
i2c_sda_pin = 4
i2c_scl_pin = 5
screen_width = 128
screen_height = 64

# GNSS UART2 pins
uart_id = 2
baud_rate = 9600
rx_pin = 26
tx_pin = 25

# --- Initialization ---
print("Initializing I2C display...")
try:
    i2c = I2C(1, sda=Pin(i2c_sda_pin), scl=Pin(i2c_scl_pin))
    oled = ssd1306.SSD1306_I2C(screen_width, screen_height, i2c)
    print("SSD1306 display initialized.")
except Exception as e:
    print(f"OLED Error: {e}")
    oled = None

print(f"Initializing UART{uart_id} for GNSS...")
gnss_serial = UART(uart_id, baudrate=baud_rate, rx=rx_pin, tx=tx_pin, timeout=1000)

def parse_nmea_coord(value, direction):
    """Converts NMEA DDMM.MMMM to decimal degrees."""
    if not value or not direction:
        return None
    try:
        # Latitude is DDMM.MMMM (2 digits for deg)
        # Longitude is DDDMM.MMMM (3 digits for deg)
        dot_idx = value.find('.')
        dd = int(value[:dot_idx-2])
        mm = float(value[dot_idx-2:])
        decimal = dd + (mm / 60)
        if direction in ['S', 'W']:
            decimal = -decimal
        return decimal
    except Exception:
        return None

def update_display(lat=None, lon=None, sats=None, msg="Wait for FIX"):
    """Update OLED with coordinate data."""
    if not oled:
        return
        
    oled.fill(0)
    oled.text("GNSS MONITOR", 0, 0)
    oled.hline(0, 10, 128, 1)
    
    if lat and lon:
        oled.text("LAT:", 0, 20)
        oled.text(f"{lat:.5f}", 40, 20)
        oled.text("LON:", 0, 32)
        oled.text(f"{lon:.5f}", 40, 32)
        if sats:
            oled.text(f"Sats: {sats}", 0, 48)
    else:
        oled.text("Status:", 0, 25)
        oled.text(msg, 0, 40)
    
    oled.show()

def main():
    update_display(msg="Initializing...")
    print("Waiting for GNSS data (NMEA)...")
    
    while True:
        try:
            if gnss_serial.any():
                line = gnss_serial.readline()
                if line:
                    try:
                        decoded_line = line.decode('ascii').strip()
                        if decoded_line.startswith('$'):
                            parts = decoded_line.split(',')
                            
                            # We look for $GPGGA or $GNGGA for position data
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
                                    if lat and lon:
                                        update_display(lat, lon, sats)
                                        print(f"FIX: Lat {lat}, Lon {lon}, Sats {sats}")
                                else:
                                    update_display(msg="No Fix (Sats: " + sats + ")")
                                    print(f"WAITING: Sats {sats}")
                                    
                    except Exception as e:
                        print(f"Parsing error: {e}")
            
            time.sleep(0.1)
            
        except KeyboardInterrupt:
            print("\nStopping...")
            update_display(msg="STOPPED")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

if __name__ == "__main__":
    main()
