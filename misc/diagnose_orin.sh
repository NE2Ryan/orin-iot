#!/bin/bash

echo "--- 1. Checking Serial Devices ---"
ls -l /dev/ttyTHS*

echo -e "
--- 2. Checking for Port Locks on /dev/ttyTHS1 ---"
sudo fuser -v /dev/ttyTHS1

echo -e "
--- 3. Checking User Groups ---"
groups

echo -e "
--- 4. Checking nvgetty Service Status ---"
systemctl is-active nvgetty
systemctl is-enabled nvgetty

echo -e "
--- 5. Checking USB Devices ---"
lsusb

echo -e "
--- 6. Testing UART Connectivity (Pin 8 to Pin 10) ---"
echo "Note: This requires a jumper between Pin 8 and 10."
# We'll just check if the device is busy for now
timeout 1s cat /dev/ttyTHS1 | xxd -l 32
