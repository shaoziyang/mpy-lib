'''
    mpy drive for LIS2DH12TR ultra-low-power high-performance 3-axis "femto" accelerometer

    Author: shaoziyang
    Date:   2026.3

    https://github.com/shaoziyang/mpy-lib

'''
from machine import I2C

LIS2DH12TR_SCALE = ('2g', '4g', '8g', '16g')
LIS2DH12TR_SENSITIVITY = [0.061, 0.122, 0.244, 0.732]

class LIS2DH12TR:
    def __init__(self, i2c, addr=24, SDO=None):
        self.i2c = i2c
        self.addr = 25 if SDO else addr
        self._scale = 0
        self.tbuf = bytearray(1)
        self.rbuf = bytearray(6)
        self.vbuf = memoryview(self.rbuf)[:1]

        self.setReg(0x20, 0x57)		# 100Hz, enable XYZ, High-resolution mode
        self.setReg(0x21, 0x00)		# normal mode
        
        self.scale('2g')
        self.x, self.y, self.z = 0, 0, 0

    # set reg
    def setReg(self, reg, dat):
        self.tbuf[0] = dat
        self.i2c.writeto_mem(self.addr, reg, self.tbuf)

    # get reg
    def getRegs(self, reg, n=1):
        self.vbuf = memoryview(self.rbuf)[:n]
        self.i2c.readfrom_mem_into(self.addr, reg, self.vbuf)

    def _int16(self, h, l):
        res = (h << 8) | l
        return res if res < 32768 else res - 65536

    def scale(self, dat=None):
        if dat is None:
            return LIS2DH12TR_SCALE[self._scale]
        if dat in LIS2DH12TR_SCALE:
            self._scale = LIS2DH12TR_SCALE.index(dat)
            self.getRegs(0x23, 1)
            self.setReg(0x23, (self.vbuf[0]&0xCF)|(self._scale<<4))

    def get_g(self):
        self.getRegs(0x28|0x80, 6)		# read XYZ registry
        rx = self._int16(self.vbuf[1], self.vbuf[0])
        ry = self._int16(self.vbuf[3], self.vbuf[2])
        rz = self._int16(self.vbuf[5], self.vbuf[4])

        self.x = rx * LIS2DH12TR_SENSITIVITY[self._scale] / 1000
        self.y = ry * LIS2DH12TR_SENSITIVITY[self._scale] / 1000
        self.z = rz * LIS2DH12TR_SENSITIVITY[self._scale] / 1000
        
        return [round(self.x,3), round(self.y,3), round(self.z,3)]
