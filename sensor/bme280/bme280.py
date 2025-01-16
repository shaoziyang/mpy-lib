"""
    mpy drive for BME280 humidity and pressure sensor

    Author: shaoziyang
    Date:   2018.2

    http://www.micropython.org.cn

"""
from machine import I2C

BME280_I2C_ADDR = const(0x76)

class BME280():
    def __init__(self, i2c, addr = BME280_I2C_ADDR):
        self.i2c = i2c
        self.addr = addr
        self.tb = bytearray(1)
        self.rb = bytearray(1)
        self.dig_T1 = self.get2Reg(0x88)
        self.dig_T2 = self.short(self.get2Reg(0x8A))
        self.dig_T3 = self.short(self.get2Reg(0x8C))
        self.dig_P1 = self.get2Reg(0x8E)
        self.dig_P2 = self.short(self.get2Reg(0x90))
        self.dig_P3 = self.short(self.get2Reg(0x92))
        self.dig_P4 = self.short(self.get2Reg(0x94))
        self.dig_P5 = self.short(self.get2Reg(0x96))
        self.dig_P6 = self.short(self.get2Reg(0x98))
        self.dig_P7 = self.short(self.get2Reg(0x9A))
        self.dig_P8 = self.short(self.get2Reg(0x9C))
        self.dig_P9 = self.short(self.get2Reg(0x9E))
        self.dig_H1 = self.getReg(0xA1)
        self.dig_H2 = self.short(self.get2Reg(0xE1))
        self.dig_H3 = self.getReg(0xE3)
        a = self.getReg(0xE5)
        self.dig_H4 = (self.getReg(0xE4)<<4)+(a%16)
        self.dig_H5 = (self.getReg(0xE6)<<4)+(a>>4)
        self.dig_H6 = self.getReg(0xE7)
        if self.dig_H6>127:
            self.dig_H6 -= 256
        self.mode = 3
        self.osrs_p = 3
        self.osrs_t = 1
        self.osrs_h = 4
        self.filter = 3
        self.setReg(0xF2, 0x04)
        self.setReg(0xF4, 0x2F)
        self.setReg(0xF5, 0x0C)
        self.T = 0
        self.P = 0
        self.H = 0
        self.version = '1.0'

    def	short(self, dat):
        if dat > 32767:
            return dat - 65536
        else:
            return dat
	
    # set reg
    def setReg(self, reg, dat):
        self.tb[0] = dat
        self.i2c.writeto_mem(self.addr, reg, self.tb)

    # get reg
    def getReg(self, reg):
        self.i2c.readfrom_mem_into(self.addr, reg, self.rb)
        return self.rb[0]
	
    # get two reg
    def	get2Reg(self, reg):
        return self.getReg(reg) + self.getReg(reg+1) * 256

    def get(self):
        adc_T = (self.getReg(0xFA)<<12) + (self.getReg(0xFB)<<4) + (self.getReg(0xFC)>>4)
        var1 = (((adc_T>>3)-(self.dig_T1<<1))*self.dig_T2)>>11
        var2 = (((((adc_T>>4)-self.dig_T1)*((adc_T>>4) - self.dig_T1))>>12)*self.dig_T3)>>14
        t = var1+var2
        self.T = ((t * 5 + 128) >> 8)/100
        var1 = (t>>1) - 64000
        var2 = (((var1>>2) * (var1>>2)) >> 11 ) * self.dig_P6
        var2 = var2 + ((var1*self.dig_P5)<<1)
        var2 = (var2>>2)+(self.dig_P4<<16)
        var1 = (((self.dig_P3*((var1>>2)*(var1>>2))>>13)>>3) + (((self.dig_P2) * var1)>>1))>>18
        var1 = ((32768+var1)*self.dig_P1)>>15
        if var1 == 0:
            return  # avoid exception caused by division by zero
        adc_P = (self.getReg(0xF7)<<12) + (self.getReg(0xF8)<<4) + (self.getReg(0xF9)>>4)
        p=((1048576-adc_P)-(var2>>12))*3125
        if p < 0x80000000:
            p = (p << 1) // var1
        else:
            p = (p // var1) *2
        var1 = (self.dig_P9 * (((p>>3)*(p>>3))>>13))>>12
        var2 = (((p>>2)) * self.dig_P8)>>13
        self.P = p + ((var1 + var2 + self.dig_P7) >> 4)
        adc_H = (self.getReg(0xFD)<<8) + self.getReg(0xFE)
        var1 = t - 76800
        var2 = (((adc_H<<14)-(self.dig_H4<<20)-(self.dig_H5*var1))+16384)>>15
        var1 = var2*(((((((var1*self.dig_H6)>>10)*(((var1*self.dig_H3)>>11)+32768))>>10)+2097152)*self.dig_H2+8192)>>14)
        var2 = var1-(((((var1>>15)*(var1>>15))>>7)*self.dig_H1)>>4)
        if var2 < 0:
            var2 = 0
        if var2 > 419430400:
            var2 = 419430400
        self.H = (var2>>12)/1024
        return [self.T, self.P, self.H]

    # get Temperature in Celsius
    def getTemp(self):
        self.get()
        return self.T

    # get Pressure in Pa
    def getPress(self):
        self.get()
        return self.P

    # get Humidity in %RH
    def getHumi(self):
        self.get()
        return self.H
    
    # Calculating absolute altitude
    def	getAltitude(self):
        return 44330*(1-(self.getPress()/101325)**(1/5.255))

    # sleep mode
    def poweroff(self):
        self.setReg(0xF4, 0)

    # normal mode
    def poweron(self):
        self.setReg(0xF4, 0x2F)
