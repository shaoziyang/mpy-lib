'''
    mpy drive for I2C LCD1602

    Author: shaoziyang
    Date:   2018.2

    https://github.com/shaoziyang/mpy-lib

'''
from time import sleep_ms

LCD_I2C_ADDR=const(63)

class I2C_LCD1602():
    def __init__(self, i2c, addr = 0):
        self.i2c=i2c
        self.buf = bytearray(1)
        self.BK, self.RS, self.E = 0x08, 0x00, 0x04
        self.ADDR = addr if addr else self.autoaddr()
        self.setcmd(0x33)
        sleep_ms(5)
        self.send(0x30)
        sleep_ms(5)
        self.send(0x20)
        sleep_ms(5)
        for i in [0x28, 0x0C, 0x06, 0x01]:
            self.setcmd(i)
        self.px, self.py = 0, 0
        self.pb = bytearray(16)
        self.version='2.1'

    def setReg(self, dat):
        self.buf[0] = dat
        self.i2c.writeto(self.ADDR, self.buf)
        sleep_ms(1)

    def send(self, dat):
        d=(dat&0xF0)|self.BK|self.RS
        self.setReg(d|0x04)
        self.setReg(d)

    def setcmd(self, cmd):
        self.RS=0
        self.send(cmd)
        self.send(cmd<<4)

    def setdat(self, dat):
        self.RS=1
        self.send(dat)
        self.send(dat<<4)

    def autoaddr(self):
        for i in range(32, 64):
            try:
                if self.i2c.readfrom(i, 1):
                    return i
            except:
                pass
        raise Exception('I2C address detect error!')

    def write_cgram(self, buf, reg=0):
        n = len(buf)
        self.setcmd(0x40 + (reg%8)*8)
        for i in range(n):
            self.setdat(buf[i])

    def clear(self):
        self.setcmd(1)

    def backlight(self, on):
        if on:
            self.BK=0x08
        else:
            self.BK=0
        self.setcmd(0)

    def on(self):
        self.setcmd(0x0C)

    def off(self):
        self.setcmd(0x08)

    def shl(self):
        self.setcmd(0x18)

    def shr(self):
        self.setcmd(0x1C)

    def newline(self):
        self.px = 0
        self.py += 1

    def print(self, s, end='\n'):
        if type(s) is not str:
            s = str(s)
        s = s + end
        for i in range(len(s)):
            d = ord(s[i])
            if d == ord('\n'):
                self.newline()
            elif d == ord('\r'):
                self.px = 0
            else:
                if self.py > 1:
                    self.py = 1
                    self.clear()
                    for j in range(16):
                        self.char(self.pb[j], j)
                        self.pb[j] = 32
                
                self.char(d, self.px, self.py)
                self.pb[self.px] = d
                if self.py:
                    self.pb[self.px] = d
                self.px += 1
                if self.px > 15:
                    self.newline()

