import ubinascii
import time
from machine import I2C
import pycom


LPS25HB_ADDRESS = 0x5D

LPS25HB_CTRL_REG1 = 0x20
LPS25HB_PRESS_OUT_XL = 0x28
LPS25HB_PRESS_OUT_L = 0x29
LPS25HB_PRESS_OUT_H = 0x2A
LPS25HB_TEMP_OUT_L = 0x2B
LPS25HB_TEMP_OUT_H = 0x2C

LPS25HB_RPDS_L = 0x39
LPS25HB_RPDS_H = 0x3A

LPS25HB_CTRL_REG1_SETUP = 0xC0  # wakeup and set measurement with a frequency of 25 Hz


class LPS25HB:
    def __init__(self, i2c):
        self.i2c = i2c
        self.address = LPS25HB_ADDRESS

        # Sensor by default in sleep mode, we have to wake it up
        i2c.writeto_mem(self.address, LPS25HB_CTRL_REG1, LPS25HB_CTRL_REG1_SETUP)

        # Calibration pressure offset
        # value = |measure - real_measure| * 16 // value is two complements
        # i2c.writeto_mem(self.address, LPS25HB_RPDS_L, value)
        # i2c.writeto_mem(self.address, LPS25HB_RPDS_H, value>>8)


    def twos_complement(self, val, bits):
        if (val & (1 << (bits - 1))) != 0: # if sign bit is set
            val = val - (1 << bits)
        return val


    def temperature_meas(self):
        buff = self.i2c.readfrom_mem(self.address, LPS25HB_TEMP_OUT_L| 0x80 , 2)
        temp = buff[1]<<8 | buff[0]
        temp = self.twos_complement(temp, 16)
        temp = 42.5 + (temp / 480.0)
        return temp


    def pressure_meas(self):
        buff = self.i2c.readfrom_mem(self.address, LPS25HB_PRESS_OUT_XL | 0x80, 3)
        press = buff[2]<<16 | buff[1]<<8 | buff[0]
        press = press/4096
        return press
