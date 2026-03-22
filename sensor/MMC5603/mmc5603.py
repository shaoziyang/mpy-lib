# MMC5603NJ 3轴地磁传感器 MicroPython 驱动

from machine import I2C
from time import sleep_ms

class MMC5603NJ:
    
    def __init__(self, i2c):
        self.i2c = i2c
        self.addr = 48
        self.tbuf = bytearray(1)
        self.rbuf = bytearray(10)
        self.vbuf = memoryview(self.rbuf)[:1]
        self.T = 0
        self.x, self.y, self.z = 0, 0, 0
        
        self.setReg(0x1C, 0x80)		# Software Reset
        sleep_ms(20)
        
        self.odr(10)				# set ODR = 10
        self.setReg(0x1B, 0xA3)		# automatic set
        self.setReg(0x1C, 0x00)		# BW=0
        self.setReg(0x1D, 0x10)		# continuous mode, periodical set
        
        self.update()
        sleep_ms(20)
    
    # set reg
    def setReg(self, reg, dat):
        self.tbuf[0] = dat
        self.i2c.writeto_mem(self.addr, reg, self.tbuf)

    # get reg
    def getRegs(self, reg, n=1):
        self.vbuf = memoryview(self.rbuf)[:n]
        self.i2c.readfrom_mem_into(self.addr, reg, self.vbuf)
        
    # output data rate
    def odr(self, ODR=10):
        self.setReg(0x1A, ODR)

    def _convert_16bit(self, out1, out0):
        return (out1<<8) + out0 - 0x8000

    def _convert_20bit(self, out2, out1, out0):
        return (out2<<12) + (out1<<4) + (out0>>4) - 0x80000
    
    def update(self, mode=''):
        if mode == 'fast':
            self.getRegs(0, 6)
            self.x = self._convert_16bit(self.vbuf[0], self.vbuf[1])
            self.y = self._convert_16bit(self.vbuf[2], self.vbuf[3])
            self.z = self._convert_16bit(self.vbuf[4], self.vbuf[5])
        else:
            self.getRegs(0, 9)
            self.x = self._convert_20bit(self.vbuf[0], self.vbuf[1], self.vbuf[6]) >>4
            self.y = self._convert_20bit(self.vbuf[2], self.vbuf[3], self.vbuf[7]) >>4
            self.z = self._convert_20bit(self.vbuf[4], self.vbuf[5], self.vbuf[8]) >>4
