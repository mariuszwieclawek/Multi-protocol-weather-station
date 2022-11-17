from machine import I2C, Timer
import ustruct
import time
import _thread


AM2320_ADDRESS = 0x5C
AM2320_READ_REG = 0x03
AM2320_WRITE_REG = 0x10
AM2320_REG_TEMP_H = 0x02
AM2320_REG_HUM_H = 0x00


class AM2320:
    def __init__(self):
        self.i2c = I2C(0, I2C.MASTER, baudrate=100000)
        self.chrono = Timer.Chrono()
        self.address = AM2320_ADDRESS
        self.hum = 0
        self.temp = 0

    def start_measurement(self, client_data):
        _thread.start_new_thread(self.am2320_thread, (client_data,)) # Start protocol choice thread

    # AM2320 sensor thread
    def am2320_thread(self, client_data):
        self.chrono.start()
        while True:
            start = self.chrono.read() # to calculate the time of measurement
            with client_data.lock:
                (hum, temp) = self.temp_and_hum_measurement()
                client_data.HUMIDITY = hum
                client_data.TEMPERATURE = temp
                client_data.MEASURE_READY = True
                print('Humidity: ', hum)
                print('Temperature: ', temp)
            end = self.chrono.read() # read elapsed time
            time.sleep(1-(end-start)) # meas every one second sleep=1-measurement_time


    def crc16(self, buff):
        crc = 0xFFFF
        for c in buff:
            crc ^= c
            for i in range(8):
                if crc & 0x01:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc


    def humidity_calc(self, hum_H, hum_L):
        return (hum_H << 8 | hum_L) * 0.1


    def temperature_calc(self, tem_H, tem_L):
        temp = ((tem_H & 0x7f) << 8 | tem_L) * 0.1
        if tem_H & 0x80:
            temp = -temp
        return temp


    def temp_and_hum_measurement(self):
        # Try wake up sensor
        try:
            self.i2c.writeto(self.address, b'')
        except OSError:
            pass # raise an exception because sensor does not respond with ACK

        # Wait at least 800us (documentation)
        time.sleep_ms(1)

        # Specify reading frame format
        """
        The host sends reading frame format：
            START + (I2C address + W) + function code (0x03) + start address + number of registers + STOP
        Host read return data:
            START + (I2C address + R) + sequential read sensor data returned + STOP
        Sensor response frame format:
            Function code (0x03) + number + data + CRC
        """
        number_of_registers = 0x04
        reading_frame_format = ustruct.pack('bbb', AM2320_READ_REG, AM2320_REG_HUM_H, number_of_registers) # create 3 bytes frame

        # Send reading frame to sensor
        self.i2c.writeto(self.address, reading_frame_format)

        # Wait at least 1.5ms (documentation)
        time.sleep_ms(2)

        # Read data response from sensor
        buff = self.i2c.readfrom_mem(self.address, 0, 8) # read 6 bytes

        # Wait at least 30us (documentation)
        time.sleep_us(50)

        # CRC calculation
        crc = buff[7]<<8 | buff[6] # little endian
        if (crc != self.crc16(buff[:-2])):
            raise Exception('AM2320 TEMPERATURE CRC ERROR')

        # Temperature and humidity calculation
        hum = self.humidity_calc(buff[2], buff[3])
        temp = self.temperature_calc(buff[4], buff[5])

        # Wait before next measurement cycle
        time.sleep_ms(100)

        return (hum, temp)


# i2c = I2C(0, I2C.MASTER, baudrate=100000)
# am2320 = AM2320(i2c)
#
# while True:
#     am2320.temp_and_hum_measurement()
#     print(am2320.hum)
#     print(am2320.temp)
