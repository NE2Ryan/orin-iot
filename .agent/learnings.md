# Project Journal

## Recent Mistakes & Corrections
- (Log failed test approaches or syntax errors here)

## Observations
- **ESP32 UART2 Pinout:** RX is GPIO 16, TX is GPIO 17. This is the standard hardware serial port for ESP32.
- **NMEA Parsing:** NEO-M8N often outputs `$GNGGA` instead of `$GPGGA` if multiple constellations (GLONASS, etc.) are enabled. The parser now handles both.
