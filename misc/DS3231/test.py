'''
    DS3231 demo

    Author: shaoziyang
    Date:   2018.3

    https://github.com/shaoziyang
'''
from machine import I2C, Pin
import DS3231

i2c = I2C(sda = Pin(5), scl=Pin(4))
ds = DS3231.DS3231(i2c)

ds.hour(12)

ds.time()
ds.time((12,10,0))

ds.datetime((2018,3,12,1,22,10,0))

ds.setALARM(12, 20, 10, DS3231.PER_DISABLE)
ds.setALARM(12, 20, 10, DS3231.PER_DAY)
ds.clearALARM()
