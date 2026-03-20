'''
    mpy drive for BMP580 Digital Pressure Sensor

    Author: shaoziyang
    Date:   2026.3

    https://github.com/shaoziyang/mpy-lib

'''
from machine import I2C

class BMP580():
    def __init__(self, i2c, addr = 70, SDO = None):
        self.i2c = i2c
        self.addr = 71 if SDO else addr
        self.tbuf = bytearray(1)
        self.rbuf = bytearray(10)
        self.vbuf = memoryview(self.rbuf)[:1]
        self.T, self.P = 0, 0
        self.setReg(0x36, 0x40)  # set press_en bit
        self.mode(1)
        self.version = '1.0'

    # set reg
    def setReg(self, reg, dat):
        self.tbuf[0] = dat
        self.i2c.writeto_mem(self.addr, reg, self.tbuf)

    # get reg
    def getRegs(self, reg, n=1):
        self.vbuf = memoryview(self.rbuf)[:n]
        self.i2c.readfrom_mem_into(self.addr, reg, self.vbuf)

    # get Temperature in Celsius
    def Temperature(self):
        self.getRegs(0x1E, 2)
        self.T = round(self.vbuf[0]/256 + self.vbuf[1], 1)
        return self.T

    # get Pressure in Pa
    def Pressure(self):
        self.getRegs(0x20, 3)
        self.P = (self.vbuf[0]>>6) + (self.vbuf[1]<<2) + (self.vbuf[2]<<10)
        return self.P

    # power mode
    def mode(self, md=1):
        self.getRegs(0x37, 1)
        self.setReg(0x37, (self.rbuf[0]&0x7c) + md)
    
    # over sampling rate
    def osr(self, OSR_P=0, OSR_T=0):
        self.getRegs(0x36, 1)
        self.setReg(0x36, (self.rbuf[0]&0xC0) + OSR_P*8 + OSR_T)

    # output data rate
    def odr(self, ODR=0):
        self.getRegs(0x37, 1)
        self.setReg(0x37, (self.rbuf[0]&0x83) + ODR*4)
