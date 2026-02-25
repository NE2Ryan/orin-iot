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

# MAG_BIAS  = (29.550, 88.050, 17.775)
# MAG_SCALE = (1.035, 0.988, 0.978)

MAG_BIAS  = (35.325, 66.525, 17.100)
MAG_SCALE = (1.029, 1.025, 0.950)

# --- True North Adjustment ---
DECLINATION = 0.0 

def main():
    print("--- Tilt-Compensated True North Dashboard ---")
    
    i2c = I2C(1, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN))
    
    try:
        oled = ssd1306.SSD1306_I2C(128, 64, i2c)
        print("OLED: OK")
    except:
        oled = None

    try:
        imu = mpu6500.MPU6500(i2c, address=0x68)
        print("MPU6500: OK")
    except Exception as e:
        print("MPU6500: Error", e)
        imu = None

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
        # Read Sensors
        accel = imu.acceleration
        m_raw = mag.magnetic
        
        # 1. Get Tilt (Roll and Pitch)
        ax, ay, az = accel
        # Math for roll and pitch
        roll = math.atan2(ay, az)
        pitch = math.atan2(-ax, math.sqrt(ay * ay + az * az))

        # 2. Process Heading
        heading = 0
        if m_raw:
            # Apply Hard/Soft Iron Calibration
            mx = (m_raw[0] - MAG_BIAS[0]) * MAG_SCALE[0]
            my = (m_raw[1] - MAG_BIAS[1]) * MAG_SCALE[1]
            mz = (m_raw[2] - MAG_BIAS[2]) * MAG_SCALE[2]
            
            # 3. Tilt Compensation Math
            # Projecting the 3D magnetic vector onto a 2D horizontal plane
            mx_h = mx * math.cos(pitch) + mz * math.sin(pitch)
            my_h = mx * math.sin(roll) * math.sin(pitch) + my * math.cos(roll) - mz * math.sin(roll) * math.cos(pitch)
            
            # 4. Calculate Final Heading
            mag_heading = math.degrees(math.atan2(mx_h, my_h))
            
            # Apply Declination for True North
            heading = mag_heading + DECLINATION
            
            # Normalize to 0-360
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
            oled.text("TRUE N", 0, 0)
            oled.text(f"{int(heading)} deg", 0, 10)

            # --- Leveler UI ---
            lx, ly, lw, lh = 75, 20, 45, 35
            oled.rect(lx, ly, lw, lh, 1)
            # Bubble position
            bubble_x = int((lx + lw/2) + (ay * (lw/2)))
            bubble_y = int((ly + lh/2) + (ax * (lh/2)))
            bx = max(lx+2, min(lx+lw-6, bubble_x))
            by = max(ly+2, min(ly+lh-6, bubble_y))
            oled.fill_rect(bx, by, 4, 4, 1)
            oled.text("TILT", 80, 0)
            
            oled.show()

        time.sleep(0.1)

if __name__ == "__main__":
    main()
