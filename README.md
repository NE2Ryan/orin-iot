# orin-iot

--- 1. Checking Serial Devices ---
crw-rw---- 1 root dialout 240, 1 Jan  1  1970 /dev/ttyTHS1
crw-rw---- 1 root dialout 240, 2 Jan  1  1970 /dev/ttyTHS2

--- 2. Checking for Port Locks on /dev/ttyTHS1 ---

--- 3. Checking User Groups ---
guest dialout sudo audio video render i2c gdm weston-launch gpio

--- 4. Checking nvgetty Service Status ---
inactive
disabled

--- 5. Checking USB Devices ---
Bus 002 Device 002: ID 0bda:0489 Realtek Semiconductor Corp. 4-Port USB 3.0 Hub
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 001 Device 003: ID 13d3:3549 IMC Networks Bluetooth Radio
Bus 001 Device 004: ID 046d:c548 Logitech, Inc. USB Receiver
Bus 001 Device 002: ID 0bda:5489 Realtek Semiconductor Corp. 4-Port USB 2.0 Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub

--- 6. Testing UART Connectivity (Pin 8 to Pin 10) ---
Note: This requires a jumper between Pin 8 and 10.
00000000: 000c 1f00 00     
