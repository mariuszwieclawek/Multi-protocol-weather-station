from machine import I2C, Timer
from network import WLAN
import pycom
import _thread
import time
import ustruct
from wifi import WIFI_CLIENT
from i2c_AM2320 import AM2320

pycom.heartbeat(False)
pycom.rgbled(0x7f0000) # Red

lock = _thread.allocate_lock()
chrono = Timer.Chrono()

HUMIDITY = 0
TEMPERATURE = 0
MEASURE_READY = False


# AM2320 sensor thread
def am2320_thread(am2320):
    global HUMIDITY
    global TEMPERATURE
    global MEASURE_READY
    chrono.start()
    while True:
        start = chrono.read() # to calculate the time of measurement
        with lock:
            am2320.temp_and_hum_measurement()
            HUMIDITY = am2320.hum
            TEMPERATURE = am2320.temp
            MEASURE_READY = True
            print('Humidity: ', HUMIDITY)
            print('Temperature: ', TEMPERATURE)
        end = chrono.read() # read elapsed time
        time.sleep(1-(end-start)) # meas every one second sleep=1-measurement_time


# WiFi client thread
def wifi_client_thread(clientsocket):
    global PRESSURE
    global TEMPERATURE
    global MEASURE_READY
    clientsocket.send('AM2320_CLIENT')
    while True:
        if MEASURE_READY == True:
            with lock:
                print('Send humidity and temperature measurement to server')
                data = ustruct.pack('ff', HUMIDITY, TEMPERATURE)
                clientsocket.send(data)
                MEASURE_READY = False
    client_socket.close()


def main():
    # initialization
    i2c = I2C(0, I2C.MASTER, baudrate=100000)
    am2320 = AM2320(i2c)

    # TODO: protocol choice
    protocol = 'WiFi'
    print('Protocol')
    if protocol == 'WiFi':
        print('WiFi')
        # Configure wifi in client mode
        wlan = WLAN(mode=WLAN.STA)
        wifi_client = WIFI_CLIENT(wlan, '192.168.4.1', 50000, )
        _thread.start_new_thread(am2320_thread, (am2320,))
        _thread.start_new_thread(wifi_client_thread, (wifi_client.client_socket,))
    elif protocol == 'Bluetooth':
        print('Bluetooth')
        pass


if __name__ == "__main__":
    main()
