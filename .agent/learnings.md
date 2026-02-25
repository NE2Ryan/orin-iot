# Project Journal

## Recent Mistakes & Corrections
- (Log failed test approaches or syntax errors here)

## Observations
- **Jetson Orin Nano UART:** Pins 8 and 10 on the 40-pin header map to `/dev/ttyTHS1` on JetPack 6.
- **Interference:** Having an ESP32 or other serial devices plugged into USB can sometimes cause noise or permission conflicts on the hardware UART ports (`/dev/ttyTHS*`).
- **NEO-M8N Default:** Standard baud rate is 9600. False positives at other speeds (like 4800) can occur due to electrical noise if the ground is not perfect.
- **ESP32 UART2 Pinout:** RX is GPIO 16, TX is GPIO 17. This is the standard hardware serial port for ESP32.
- **NMEA Parsing:** NEO-M8N often outputs `$GNGGA` instead of `$GPGGA` if multiple constellations (GLONASS, etc.) are enabled. The parser now handles both.
