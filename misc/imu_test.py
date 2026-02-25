from machine import Pin, I2C
import ssd1306
import mpu6500
import ak8963
import time
import math

# --- Configuration ---
I2C_SDA = 4
I2C_SCL = 5

# --- Initialization ---
print("Initializing I2C Bus...")
i2c = I2C(1, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL))

# Scan for devices to verify connections
devices = i2c.scan()
print(f"I2C Scan found: {[hex(d) for d in devices]}")

# 1. Initialize OLED
try:
    oled = ssd1306.SSD1306_I2C(128, 64, i2c)
    print("OLED Ready")
except:
    oled = None

# 2. Initialize MPU6500 (Accel/Gyro)
# This driver automatically enables Bypass Mode for the Magnetometer
try:
    imu = mpu6500.MPU6500(i2c, address=0x68)
    print("MPU6500 Ready")
except Exception as e:
    print(f"MPU6500 Error: {e}")
    imu = None

# 3. Initialize AK8963 (Magnetometer)
try:
    # Magnetometer is at 0x0C
    mag = ak8963.AK8963(i2c, address=0x0C)
    print("AK8963 Magnetometer Ready")
except Exception as e:
    print(f"Magnetometer Error: {e} (Is bypass enabled?)")
    mag = None

def main():
    print("Starting IMU/Mag Test...")
    while True:
        # Get Data
        accel = imu.acceleration if imu else (0,0,0)
        m_data = mag.magnetic if mag else None
        
        heading = 0
        if m_data:
            mx, my, mz = m_data
            heading = math.degrees(math.atan2(my, mx))
            if heading < 0: heading += 360

        # Serial Output
        print(f"Heading: {heading:3.1f} | Accel: {accel}")

        # OLED Output
        if oled:
            oled.fill(0)
            oled.text("IMU & MAG TEST", 0, 0)
            oled.hline(0, 10, 128, 1)
            
            oled.text(f"Heading: {int(heading)} deg", 0, 20)
            oled.text(f"AX: {accel[0]:.2f}", 0, 35)
            oled.text(f"AY: {accel[1]:.2f}", 0, 45)
            oled.text(f"AZ: {accel[2]:.2f}", 0, 55)
            
            # Simple visualization of tilt
            bubble_x = 100 + int(accel[1] * 20)
            oled.fill_rect(90, 35, 20, 20, 1)
            oled.fill_rect(bubble_x-2, 43, 4, 4, 0)
            
            oled.show()
            
        time.sleep(0.1)

if __name__ == "__main__":
    main()
