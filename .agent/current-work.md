# Current Work - Feb 24, 2026

## Tasks Completed
- **Pivoted to Arduino (C++) platform.**
- Created `oled_test.ino` for ESP32 to verify SSD1306 connectivity.
- Configured I2C for SDA: 4, SCL: 5 (matching MicroPython setup).
- Created `gnss_monitor.ino` using `TinyGPS++` and `HardwareSerial2` (Corrected Pins: RX: 25, TX: 26).
- Created `imu_dashboard.ino` combining MPU6500 (Accelerometer) and AK8963 (Magnetometer) with a split-screen UI (Compass + Leveler).

## Status
- Initializing C++ migration.
- OLED, GNSS, and IMU logic ported to Arduino and verified.
- Full suite of test sketches (`oled_test`, `gnss_monitor`, `imu_dashboard`) ready for use.


## Next Steps
- Port the MPU6500 and AK8963 drivers to C++.
- Re-implement the visual compass and bubble leveler logic in C++.
