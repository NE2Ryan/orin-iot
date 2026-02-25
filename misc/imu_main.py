from machine import Pin, I2C
import ssd1306
import mpu6500
import ak8963
import time
import math

# --- Configuration ---
i2c_sda_pin = 4
i2c_scl_pin = 5
screen_width = 128
screen_height = 64

# --- Initialization ---
print("Initializing I2C Bus...")
i2c = I2C(1, sda=Pin(i2c_sda_pin), scl=Pin(i2c_scl_pin))

# Scan for devices
devices = i2c.scan()
print(f"I2C scan found devices at addresses: {[hex(d) for d in devices]}")

# Initialize OLED
try:
    oled = ssd1306.SSD1306_I2C(screen_width, screen_height, i2c)
    print("OLED initialized.")
except Exception as e:
    print(f"OLED Error: {e}")
    oled = None

# Initialize MPU (must be first to enable bypass)
try:
    imu = mpu6500.MPU6500(i2c, address=0x68)
    print("MPU6500 initialized.")
except Exception as e:
    print(f"MPU Error: {e}")
    imu = None

# Initialize Magnetometer
try:
    mag = ak8963.AK8963(i2c, address=0x0C)
    print("Magnetometer initialized.")
except Exception as e:
    print(f"Magnetometer Error: {e}")
    mag = None

def draw_ui(heading, accel):
    if not oled:
        return
    
    oled.fill(0)
    
    # --- Left Side: Compass (Center 32, 32) ---
    lcx, lcy = 32, 32
    r = 20
    oled.text("N", lcx-4, lcy-r-8)
    oled.text("S", lcx-4, lcy+r+2)
    
    rad = math.radians(-heading)
    nx = int(lcx + r * math.sin(rad))
    ny = int(lcy - r * math.cos(rad))
    oled.line(lcx, lcy, nx, ny, 1)
    oled.text(f"H:{int(heading)}", 0, 0)

    # --- Right Side: Leveller (Center 96, 32) ---
    rcx, rcy = 96, 32
    l_size = 25
    # Draw crosshair
    oled.hline(rcx - l_size, rcy, l_size * 2, 1)
    oled.vline(rcx, rcy - l_size, l_size * 2, 1)
    oled.rect(rcx - l_size, rcy - l_size, l_size * 2, l_size * 2, 1)
    
    # Calculate bubble position from Accel (X and Y)
    # Assuming board is flat when Ax=0, Ay=0
    ax, ay, az = accel
    # Sensitivity: 1G tilt moves bubble to edge
    bx = int(rcx + (ay * l_size)) 
    by = int(rcy + (ax * l_size))
    
    # Constrain bubble to box
    bx = max(rcx - l_size, min(rcx + l_size, bx))
    by = max(rcy - l_size, min(rcy + l_size, by))
    
    # Draw bubble (small 4x4 square)
    oled.fill_rect(bx-2, by-2, 4, 4, 1)
    oled.text("LEVEL", rcx-20, 0)
    
    oled.show()

def main():
    print("Reading IMU and Magnetometer data...")
    print("Format: Accel(x,y,z) | Gyro(x,y,z) | Mag(x,y,z) | Heading")
    
    while True:
        try:
            accel = imu.acceleration if imu else (0,0,0)
            gyro = imu.gyro if imu else (0,0,0)
            m_data = mag.magnetic if mag else None
            
            heading = 0
            if m_data:
                mx, my, mz = m_data
                heading = math.degrees(math.atan2(my, mx))
                if heading < 0:
                    heading += 360
            
            # Print to REPL
            print(f"A:{accel} | G:{gyro} | M:{m_data} | H:{heading:3.1f}")
            
            # Update Visual UI
            draw_ui(heading, accel)
            
            time.sleep(0.1)
        except KeyboardInterrupt:
            print("Stopping...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
