from machine import I2C
from network import WLAN
import pycom
from i2c_AM2320 import AM2320

pycom.heartbeat(False)
pycom.rgbled(0x00FF00)  # Green led


def main():
    i2c = I2C(0, I2C.MASTER, baudrate=100000)
    am2320 = AM2320(i2c)
    am2320.temp_and_hum_measurement()
    print(am2320.hum)
    print(am2320.temp)


if __name__ == "__main__":
    main()
