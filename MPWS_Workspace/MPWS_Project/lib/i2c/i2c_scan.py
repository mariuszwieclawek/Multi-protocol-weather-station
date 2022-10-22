import time
from machine import I2C
import pycom

pycom.heartbeat(False)
pycom.rgbled(0x7f0000) # red
# pycom.rgbled(0x00FF00)  # Green
# pycom.rgbled(0x0000FF)  # Blue

i2c = I2C(0, I2C.MASTER, baudrate=100000)
addr = []
while True:
    try:
        addr=i2c.scan()[0]
    except IndexError:
        print('Not found any i2c device')
    else:
        print(hex(addr))
    time.sleep(1)
