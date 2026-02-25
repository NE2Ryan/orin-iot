import machine

class MPU6500:
    def __init__(self, i2c, address=0x68):
        self.i2c = i2c
        self.address = address
        self.init_sensor()

    def init_sensor(self):
        # Wake up the MPU6500
        self.i2c.writeto_mem(self.address, 0x6B, b'\x00')
        # Enable I2C bypass to access AK8963 magnetometer
        self.i2c.writeto_mem(self.address, 0x37, b'\x02')

    def _read_word(self, reg):
        data = self.i2c.readfrom_mem(self.address, reg, 2)
        # Convert to signed 16-bit integer
        value = (data[0] << 8) | data[1]
        if value > 32767:
            value -= 65536
        return value

    @property
    def acceleration(self):
        """Returns (x, y, z) acceleration in Gs (assuming +/- 2g range)"""
        raw_x = self._read_word(0x3B)
        raw_y = self._read_word(0x3D)
        raw_z = self._read_word(0x3F)
        # 16384 is the LSB/g for +/- 2g range
        return (raw_x / 16384.0, raw_y / 16384.0, raw_z / 16384.0)

    @property
    def gyro(self):
        """Returns (x, y, z) gyroscope values in deg/s (assuming +/- 250 deg/s)"""
        raw_x = self._read_word(0x43)
        raw_y = self._read_word(0x45)
        raw_z = self._read_word(0x47)
        # 131.0 is the LSB/(deg/s) for +/- 250 deg/s range
        return (raw_x / 131.0, raw_y / 131.0, raw_z / 131.0)
