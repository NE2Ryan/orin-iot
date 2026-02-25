from machine import Pin, I2C, UART
import ssd1306
import mpu6500
import ak8963
import time
import math

# --- Configuration ---
I2C_SDA, I2C_SCL = 4, 5
UART_ID, RX_PIN, TX_PIN, BAUD = 2, 26, 25, 9600

# --- User Calibration ---
MAG_BIAS  = (35.325, 66.525, 17.100)
MAG_SCALE = (1.029, 1.025, 0.950)
DECLINATION = 0.0 

# --- Global State ---
gnss = {"lat": 0.0, "lon": 0.0, "sats": "0", "fix": False}

# --- Initialization ---
i2c = I2C(1, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL))
gps = UART(UART_ID)
gps.init(BAUD, bits=8, parity=None, stop=1, rx=RX_PIN, tx=TX_PIN)

oled = ssd1306.SSD1306_I2C(128, 64, i2c)
imu = mpu6500.MPU6500(i2c, address=0x68)
mag = ak8963.AK8963(i2c, address=0x0C)

def parse_coord(v, d):
    if not v or not d: return 0.0
    try:
        dot = v.find('.')
        dd, mm = int(v[:dot-2]), float(v[dot-2:])
        res = dd + (mm/60)
        return -res if d in 'SW' else res
    except: return 0.0

def update_gps():
    if gps.any():
        line = gps.readline()
        try:
            msg = line.decode('ascii').strip()
            if msg.startswith('$GNGGA') or msg.startswith('$GPGGA'):
                p = msg.split(',')
                gnss["sats"] = p[7]
                if p[6] != '0':
                    gnss["lat"], gnss["lon"], gnss["fix"] = parse_coord(p[2], p[3]), parse_coord(p[4], p[5]), True
                else: gnss["fix"] = False
        except: pass

def draw_ui(hd, acc):
    oled.fill(0)
    
    # --- TOP LINE ---
    f_stat = "FIX" if gnss["fix"] else "..."
    oled.text(f"H:{int(hd):3d} {f_stat} S:{gnss['sats']}", 0, 0)
    oled.hline(0, 9, 128, 1)

    # --- COMPASS (Left) ---
    cx, cy, r = 25, 38, 22
    rad = math.radians(-hd)
    # Needle
    oled.line(cx, cy, int(cx+r*math.sin(rad)), int(cy-r*math.cos(rad)), 1)
    # Outer Frame
    oled.rect(cx-r, cy-r, r*2, r*2, 1)

    # --- DATA (Right) ---
    oled.text(f"L:{gnss['lat']:.4f}", 55, 15)
    oled.text(f"O:{gnss['lon']:.4f}", 55, 25)
    
    # --- LEVELER (Bottom Right) ---
    oled.text("TILT", 55, 40)
    lx, ly, lw, lh = 55, 50, 65, 10
    oled.rect(lx, ly, lw, lh, 1)
    bx = max(lx+2, min(lx+lw-6, int((lx+lw/2) + (acc[1]*lw/2))))
    oled.fill_rect(bx, ly+2, 4, lh-4, 1)
    
    oled.show()

def main():
    while True:
        update_gps()
        acc = imu.acceleration
        m = mag.magnetic
        heading = 0
        if m:
            ax, ay, az = acc
            roll, pitch = math.atan2(ay, az), math.atan2(-ax, math.sqrt(ay*ay + az*az))
            mx = (m[0]-MAG_BIAS[0])*MAG_SCALE[0]
            my = (m[1]-MAG_BIAS[1])*MAG_SCALE[1]
            mz = (m[2]-MAG_BIAS[2])*MAG_SCALE[2]
            mx_h = mx*math.cos(pitch) + mz*math.sin(pitch)
            my_h = mx*math.sin(roll)*math.sin(pitch) + my*math.cos(roll) - mz*math.sin(roll)*math.cos(pitch)
            # Use user-discovered axis swap
            heading = (math.degrees(math.atan2(mx_h, my_h)) + DECLINATION) % 360
        
        draw_ui(heading, acc)
        time.sleep(0.05)

if __name__ == "__main__":
    main()
