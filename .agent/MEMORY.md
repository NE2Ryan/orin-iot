# Persistent Working Context

## Environment Setup & Gotchas
- **Platform:** ESP32 (Arduino / C++)
- **I2C Pinout:** SDA: GPIO 4, SCL: GPIO 5
- **GNSS Pinout:** RX: GPIO 25, TX: GPIO 26 (UART2) - *Corrected after debug*
- **Display:** SSD1306 (128x64) via Adafruit SSD1306 library.

## Proven Patterns
- Using `Adafruit_GFX` and `Adafruit_SSD1306` for display handling.
- Using `TinyGPS++` for NMEA parsing on ESP32 `HardwareSerial(2)`.
