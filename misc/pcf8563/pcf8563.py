'''
    PCF8563 RTC drive

    Author: shaoziyang
    Date:   2021.1

    https://github.com/shaoziyang
'''
from micropython import const

PCF8563_I2C_ADDRESS  = const(81)
PCF8563_REG_CTRL1    = const(0)
PCF8563_REG_CTRL2    = const(1)
PCF8563_REG_SECOND   = const(2)
PCF8563_REG_MINUTE   = const(3)
PCF8563_REG_HOUR     = const(4)
PCF8563_REG_WEEKDAY  = const(6)
PCF8563_REG_DAY      = const(5)
PCF8563_REG_MONTH    = const(7)
PCF8563_REG_YEAR     = const(8)

class PCF8563():
    def __init__(self, i2c):
        self.i2c = i2c
        self.tb = bytearray(1)
        self.rb = bytearray(1)
        self.buf = bytearray(7)
        self.DT = [0] * 8
        self.setReg(PCF8563_REG_CTRL1, 0)  # start rtc
        self.setReg(PCF8563_REG_CTRL2, 0)  # disable int

    # set reg
    def setReg(self, reg, dat):
        self.tb[0] = dat
        self.i2c.writeto_mem(PCF8563_I2C_ADDRESS, reg, self.tb)

    # get reg
    def getReg(self, reg):
        self.i2c.readfrom_mem_into(PCF8563_I2C_ADDRESS, reg, self.rb)
        return self.rb[0]

    def DecToHex(self, dat):
        return (dat//10) * 16 + (dat%10)

    def HexToDec(self, dat):
        return (dat//16) * 10 + (dat%16)

    def year(self, year = None):
        if year == None:
            return self.HexToDec(self.getReg(PCF8563_REG_YEAR)) + 2000
        else:
            self.setReg(PCF8563_REG_YEAR, self.DecToHex(year%100))

    def month(self, month = None):
        if month == None:
            return self.HexToDec(self.getReg(PCF8563_REG_MONTH)%32)
        else:
            self.setReg(PCF8563_REG_MONTH, self.DecToHex(month%13))

    def day(self, day = None):
        if day == None:
            return self.HexToDec(self.getReg(PCF8563_REG_DAY)%64)
        else:
            self.setReg(PCF8563_REG_DAY, self.DecToHex(day%32))

    def weekday(self, weekday = None):
        if weekday == None:
            return self.HexToDec(self.getReg(PCF8563_REG_WEEKDAY)%8)
        else:
            self.setReg(PCF8563_REG_WEEKDAY, self.DecToHex(weekday%8))

    def hour(self, hour = None):
        if hour == None:
            return self.HexToDec(self.getReg(PCF8563_REG_HOUR)%64)
        else:
            self.setReg(PCF8563_REG_HOUR, self.DecToHex(hour%24))

    def minute(self, minute = None):
        if minute == None:
            return self.HexToDec(self.getReg(PCF8563_REG_MINUTE)%128)
        else:
            self.setReg(PCF8563_REG_MINUTE, self.DecToHex(minute%60))

    def second(self, second = None):
        if second == None:
            return self.HexToDec(self.getReg(PCF8563_REG_SECOND)%128)
        else:
            self.setReg(PCF8563_REG_SECOND, self.DecToHex(second%60))

    def datetime(self, DT=None):
        if DT == None: # get
            self.i2c.readfrom_mem_into(PCF8563_I2C_ADDRESS, PCF8563_REG_SECOND, self.buf)
            self.DT[0] = self.HexToDec(self.buf[6]) + 2000
            self.DT[1] = self.HexToDec(self.buf[5]%32)
            self.DT[2] = self.HexToDec(self.buf[3]%64)
            self.DT[3] = self.HexToDec(self.buf[4]%8)
            self.DT[4] = self.HexToDec(self.buf[2]%64)
            self.DT[5] = self.HexToDec(self.buf[1]%128)
            self.DT[6] = self.HexToDec(self.buf[0]%128)
            self.DT[7] = 0
            return self.DT
        else:          # set
            self.buf[0] = self.DecToHex(DT[6]%60)    # second
            self.buf[1] = self.DecToHex(DT[5]%60)    # minute
            self.buf[2] = self.DecToHex(DT[4]%24)    # hour
            self.buf[3] = self.DecToHex(DT[2]%32)    # date
            self.buf[4] = self.DecToHex(DT[3]%8)     # week day
            self.buf[5] = self.DecToHex(DT[1]%13)    # month
            self.buf[6] = self.DecToHex(DT[0]%100)   # year
            self.i2c.writeto_mem(PCF8563_I2C_ADDRESS, PCF8563_REG_SECOND, self.buf) 
