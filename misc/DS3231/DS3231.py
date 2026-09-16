'''
    DS3231 RTC drive

    Author: shaoziyang
    Date:   2018.3
    Update: 2026.9

    https://github.com/shaoziyang
'''
from micropython import const

DS3231_I2C_ADDR   = const(0x68)
DS3231_REG_SEC    = const(0x00)
DS3231_REG_MIN    = const(0x01)
DS3231_REG_HOUR   = const(0x02)
DS3231_REG_WEEKDAY= const(0x03)
DS3231_REG_DAY    = const(0x04)
DS3231_REG_MONTH  = const(0x05)
DS3231_REG_YEAR   = const(0x06)
DS3231_REG_A1SEC  = const(0x07)
DS3231_REG_A1MIN  = const(0x08)
DS3231_REG_A1HOUR = const(0x09)
DS3231_REG_A1DAY  = const(0x0A)
DS3231_REG_A2MIN  = const(0x0B)
DS3231_REG_A2HOUR = const(0x0C)
DS3231_REG_A2DAY  = const(0x0D)
DS3231_REG_CTRL   = const(0x0E)
DS3231_REG_STA    = const(0x0F)
DS3231_REG_AGOFF  = const(0x10)
DS3231_REG_TEMP   = const(0x11)

PER_DISABLE = const(0)
PER_MINUTE  = const(1)
PER_HOUR    = const(2)
PER_DAY     = const(3)
PER_WEEKDAY = const(4)
PER_MONTH   = const(5)

class DS3231():
    def __init__(self, i2c):
        self.i2c = i2c
        self.buf = bytearray(1)

    def DecToHex(self, dat):
        return (dat//10) * 16 + (dat%10)

    def HexToDec(self, dat):
        return (dat//16) * 10 + (dat%16)

    def setReg(self, reg, dat):
        self.buf[0] = dat
        self.i2c.writeto_mem(DS3231_I2C_ADDR, reg, self.buf)

    def getReg(self, reg):
        self.i2c.readfrom_mem_into(DS3231_I2C_ADDR, reg, self.buf)
        return self.buf[0]

    def second(self, sec = None):
        if sec == None:
            return self.HexToDec(self.getReg(DS3231_REG_SEC))
        else:
            self.setReg(DS3231_REG_SEC, self.DecToHex(sec%60))

    def minute(self, minute = None):
        if minute == None:
            return self.HexToDec(self.getReg(DS3231_REG_MIN))
        else:
            self.setReg(DS3231_REG_MIN, self.DecToHex(minute%60))

    def hour(self, hour = None):
        if hour == None:
            return self.HexToDec(self.getReg(DS3231_REG_HOUR))
        else:
            self.setReg(DS3231_REG_HOUR, self.DecToHex(hour%24))

    def weekday(self, weekday = None):
        if weekday == None:
            return self.HexToDec(self.getReg(DS3231_REG_WEEKDAY))
        else:
            self.setReg(DS3231_REG_WEEKDAY, self.DecToHex(weekday%8))

    def day(self, day = None):
        if day == None:
            return self.HexToDec(self.getReg(DS3231_REG_DAY))
        else:
            self.setReg(DS3231_REG_DAY, self.DecToHex(day%32))

    def month(self, month = None):
        if month == None:
            return self.HexToDec(self.getReg(DS3231_REG_MONTH))
        else:
            self.setReg(DS3231_REG_MONTH, self.DecToHex(month%13))

    def year(self, year = None):
        if year == None:
            return self.HexToDec(self.getReg(DS3231_REG_YEAR)) + 2000
        else:
            self.setReg(DS3231_REG_YEAR, self.DecToHex(year%100))

    def date(self, dat = None):
        if dat == None:
            return (self.year(), self.month(), self.day())
        else:
            self.year(dat[0]%100)
            self.month(dat[1]%13)
            self.day(dat[2]%32)

    def time(self, dat = None):
        if dat == None:
            return (self.hour(), self.minute(), self.second())
        else:
            self.hour(dat[0]%24)
            self.minute(dat[1]%60)
            self.second(dat[2]%60)

    def datetime(self, dat = None):
        if dat == None:
            return self.date() + (self.weekday(),) + self.time() + (0,)
        else:
            self.year(dat[0])
            self.month(dat[1])
            self.day(dat[2])
            self.weekday(dat[3])
            self.hour(dat[4])
            self.minute(dat[5])
            self.second(dat[6])

    def setALARM(self, day, hour, minute, repeat):
        IE = self.getReg(DS3231_REG_CTRL)
        if repeat == PER_DISABLE:
            self.setReg(DS3231_REG_CTRL, IE & 0xFC) # disable ALARM OUT
            return
        IE |= 0x46
        self.setReg(DS3231_REG_CTRL, IE)
        M2 = M3 = M4 = 0x80
        DT = 0
        if repeat == PER_MINUTE:
            pass
        elif repeat == PER_HOUR:
            M2 = 0
        elif repeat == PER_DAY:
            M2 = M3 = 0
        else:
            M2 = M3 = M4 = 0
            if repeat == PER_WEEKDAY:
                DT = 0x40
        self.setReg(DS3231_REG_A2MIN,  self.DecToHex(minute%60)|M2)
        self.setReg(DS3231_REG_A2HOUR, self.DecToHex(hour%24)|M3)
        self.setReg(DS3231_REG_A2DAY,  self.DecToHex(day%32)|M4|DT)

    def clearALARM(self):
        self.setReg(DS3231_REG_STA, 0)

    def temperature(self):
        t1 = self.getReg(DS3231_REG_TEMP)
        t2 = self.getReg(DS3231_REG_TEMP + 1)
        if t1>0x7F:
            return t1 - t2/256 -256
        else:
            return t1 + t2/256
