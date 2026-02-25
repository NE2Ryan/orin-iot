# Project Journal

## Recent Mistakes & Corrections
- (Log failed test approaches or syntax errors here)

## Observations
- **Jetson Orin Nano UART:** Pins 8 and 10 on the 40-pin header map to `/dev/ttyTHS1`. `/dev/ttyTHS0` is generally unavailable or assigned to the serial console.
- **ESP32 UART2 Pinout:** RX is GPIO 16, TX is GPIO 17. This is the standard hardware serial port for ESP32.
- **NMEA Parsing:** NEO-M8N often outputs `$GNGGA` instead of `$GPGGA` if multiple constellations (GLONASS, etc.) are enabled. The parser now handles both.
