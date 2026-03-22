# [mpy-lib](https://github.com/micropython-Chinese-Community/mpy-lib)

## MMC5603 3-axis Magnetic Sensor

- [DataSheet](
https://www.memsic.com/Public/Uploads/uploadfile/files/20220119/MMC5603NJDatasheetRev.B.pdf)

The MMC5603NJ is a monolithic complete 3-axis AMR magnetic sensor with  on-chip signal processing and integrated digital bus (I 2 C fast mode and I3C interface), the device can be connected directly to a microprocessor,  eliminating the need for A/D converters or timing resources. 

## Example


```py
from machine import I2C, Pin
from time import sleep_ms

from MMC5603 import MMC5603

i2c = I2C(0, sda=Pin(4), scl=Pin(16))

m = MMC5603(i2c)

while 1:
    sleep_ms(500)
    m.update()
    print(m.x, m.y, m.z)

```
