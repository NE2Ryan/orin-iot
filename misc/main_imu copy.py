from machine import Pin, I2C
import ssd1306
import mpu6500
import ak8963
import time
import math

# --- Configuration ---
SDA_PIN = 4
SCL_PIN = 5

# --- Calibration Constants ---
# MAG_BIAS  = (51.300, 62.400, 22.200)
# MAG_SCALE = (0.978, 1.031, 0.993)

MAG_BIAS  = (29.550, 88.050, 17.775)
MAG_SCALE = (1.035, 0.988, 0.978)

# --- True North Adjustment ---
# Find your declination at magnetic-declination.com
# Example: If your declination is +2.5, set to 2.5
DECLINATION = 0.0 

def main():
    print("--- True North IMU Dashboard ---")
    
    # 1. Initialize I2C
    i2c = I2C(1, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN))
    
    # 2. Scan for devices
    devices = i2c.scan()
    print("I2C Scan results:", [hex(d) for d in devices])
    
    # 3. Initialize OLED
    try:
        oled = ssd1306.SSD1306_I2C(128, 64, i2c)
        print("OLED: OK")
    except:
        oled = None

    # 4. Initialize MPU6500
    try:
        imu = mpu6500.MPU6500(i2c, address=0x68)
        print("MPU6500: OK")
    except Exception as e:
        print("MPU6500: Error", e)
        imu = None

    # 5. Initialize AK8963 (Magnetometer)
    try:
        mag = ak8963.AK8963(i2c, address=0x0C)
        print("AK8963: OK")
    except Exception as e:
        print("AK8963: Error", e)
        mag = None

    if not imu or not mag:
        print("CRITICAL: Sensors not detected.")
        return

    while True:
        # Read Data
        accel = imu.acceleration
        m_raw = mag.magnetic
        
        # Apply Calibration
        heading = 0
        if m_raw:
            # Formula: (Raw - Bias) * Scale
            mx = (m_raw[0] - MAG_BIAS[0]) * MAG_SCALE[0]
            my = (m_raw[1] - MAG_BIAS[1]) * MAG_SCALE[1]
            mz = (m_raw[2] - MAG_BIAS[2]) * MAG_SCALE[2]
            
            # 1. Calculate Magnetic Heading
            # Swapping X and Y to align with user's specific sensor orientation
            mag_heading = math.degrees(math.atan2(mx, my))
            
            # 2. Convert to True Heading
            heading = mag_heading + DECLINATION
            
            # 3. Normalize to 0-360
            if heading < 0: heading += 360
            if heading >= 360: heading -= 360

        # Update OLED
        if oled:
            oled.fill(0)
            
            # --- Compass UI ---
            cx, cy, r = 32, 35, 25
            oled.text("N", cx-4, cy-r-8)
            rad = math.radians(-heading)
            nx = int(cx + r * math.sin(rad))
            ny = int(cy - r * math.cos(rad))
            oled.line(cx, cy, nx, ny, 1)
            oled.text("COMPASS", 0, 0)
            oled.text(f"{int(heading)} deg", 0, 10)

            # --- Leveler UI ---
            lx, ly, lw, lh = 75, 20, 45, 35
            oled.rect(lx, ly, lw, lh, 1)
            bubble_x = int((lx + lw/2) + (accel[1] * (lw/2)))
            bubble_y = int((ly + lh/2) + (accel[0] * (lh/2)))
            bx = max(lx+2, min(lx+lw-6, bubble_x))
            by = max(ly+2, min(ly+lh-6, bubble_y))
            oled.fill_rect(bx, by, 4, 4, 1)
            oled.text("LEVEL", 80, 0)
            
            oled.show()

        print(f"H: {heading:3.1f} | Accel: {accel}")
        time.sleep(0.1)

if __name__ == "__main__":
    main()
