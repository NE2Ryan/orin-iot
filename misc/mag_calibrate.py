from machine import Pin, I2C
import mpu6500
import ak8963
import time

# --- Configuration ---
SDA_PIN = 4
SCL_PIN = 5

def calibrate():
    i2c = I2C(1, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN))
    
    # Initialize MPU to enable bypass
    print("Initializing MPU6500...")
    imu = mpu6500.MPU6500(i2c)
    
    print("Initializing AK8963 Magnetometer...")
    mag = ak8963.AK8963(i2c)
    
    # Setup tracking variables
    mag_mins = [1000, 1000, 1000]
    mag_maxs = [-1000, -1000, -1000]
    
    print("--- CALIBRATION START ---")
    print("Rotate the sensor in ALL directions (Figure-8) for 60 seconds.")
    print("Ensure you point it Up, Down, Left, Right, Front, Back.")
    
    start_time = time.time()
    last_print = 0
    
    while (time.time() - start_time) < 60:
        m = mag.magnetic
        if m:
            for i in range(3):
                if m[i] < mag_mins[i]: mag_mins[i] = m[i]
                if m[i] > mag_maxs[i]: mag_maxs[i] = m[i]
        
        # Print progress every second
        if time.time() - last_print >= 1:
            elapsed = time.time() - start_time
            print("Time: {:2d}/60s | Min: ({:5.1f}, {:5.1f}, {:5.1f}) | Max: ({:5.1f}, {:5.1f}, {:5.1f})".format(
                int(elapsed), mag_mins[0], mag_mins[1], mag_mins[2], 
                mag_maxs[0], mag_maxs[1], mag_maxs[2]))
            last_print = time.time()
            
        time.sleep(0.05)

    print("--- CALIBRATION COMPLETE ---")
    
    # Calculate Hard Iron Bias (Offsets)
    bias = [
        (mag_maxs[0] + mag_mins[0]) / 2,
        (mag_maxs[1] + mag_mins[1]) / 2,
        (mag_maxs[2] + mag_mins[2]) / 2
    ]
    
    # Calculate Soft Iron Scale Factors
    # First get the scale (radius) for each axis
    delta_x = (mag_maxs[0] - mag_mins[0]) / 2
    delta_y = (mag_maxs[1] - mag_mins[1]) / 2
    delta_z = (mag_maxs[2] - mag_mins[2]) / 2
    
    avg_delta = (delta_x + delta_y + delta_z) / 3
    
    scale = [
        avg_delta / delta_x if delta_x != 0 else 1,
        avg_delta / delta_y if delta_y != 0 else 1,
        avg_delta / delta_z if delta_z != 0 else 1
    ]

    print("--- COPY THESE VALUES ---")
    print("BIAS  = ({:.3f}, {:.3f}, {:.3f})".format(bias[0], bias[1], bias[2]))
    print("SCALE = ({:.3f}, {:.3f}, {:.3f})".format(scale[0], scale[1], scale[2]))
    print("--------------------------")

if __name__ == "__main__":
    calibrate()
