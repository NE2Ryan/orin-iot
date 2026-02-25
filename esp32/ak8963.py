import machine
import time

class AK8963:
    def __init__(self, i2c, address=0x0C):
        self.i2c = i2c
        self.address = address
        self.init_sensor()

    def init_sensor(self):
        # Power down first
        self.i2c.writeto_mem(self.address, 0x0A, b'\x00')
        time.sleep(0.01)
        # Set to Continuous measurement mode 2 (100Hz, 16-bit)
        self.i2c.writeto_mem(self.address, 0x0A, b'\x16')
        time.sleep(0.01)

    def _read_word(self, reg):
        # AK8963 is little-endian (unlike MPU)
        data = self.i2c.readfrom_mem(self.address, reg, 2)
        value = (data[1] << 8) | data[0]
        if value > 32767:
            value -= 65536
        return value

    @property
    def magnetic(self):
        """Returns (x, y, z) magnetic field in uT"""
        # Check ST1 register if data is ready
        st1 = self.i2c.readfrom_mem(self.address, 0x02, 1)[0]
        if not (st1 & 0x01):
            return None # Data not ready
            
        raw_x = self._read_word(0x03)
        raw_y = self._read_word(0x05)
        raw_z = self._read_word(0x07)
        
        # Read ST2 to finish the measurement
        self.i2c.readfrom_mem(self.address, 0x09, 1)
        
        # Scale for 16-bit (0.15 uT/LSB)
        scale = 0.15
        return (raw_x * scale, raw_y * scale, raw_z * scale)
