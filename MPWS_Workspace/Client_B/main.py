from machine import I2C, Timer
from network import WLAN
import pycom
import _thread
import time
import ustruct
from wifi import WIFI_CLIENT
from i2c_LPS25HB import LPS25HB

pycom.heartbeat(False)
pycom.rgbled(0x0000FF)  # Blue

lock = _thread.allocate_lock()
chrono = Timer.Chrono()

PRESSURE = 0
TEMPERATURE = 0
MEASURE_READY = False

# LPS25HB sensor thread
def lps25hb_thread(lps25hb):
    global PRESSURE
    global TEMPERATURE
    global MEASURE_READY
    chrono.start()
    while True:
        start = chrono.read() # to calculate the time of measurement
        with lock:
            PRESSURE = lps25hb.pressure_meas()
            TEMPERATURE = lps25hb.temperature_meas()
            MEASURE_READY = True
            print('PRESSURE: ', PRESSURE)
            print('TEMPERATURE: ', TEMPERATURE)
        end = chrono.read() # read elapsed time
        time.sleep(1-(end-start)) # meas every one second sleep=1-measurement_time



# WiFi client thread
def wifi_client_thread(clientsocket):
    global PRESSURE
    global TEMPERATURE
    global MEASURE_READY
    clientsocket.send('LPS25HB_CLIENT')
    while True:
        if MEASURE_READY == True: # when measure is ready
            with lock:
                print('Send pressure and temperature measurement to server')
                data = ustruct.pack('ff', PRESSURE, TEMPERATURE)
                clientsocket.send(data)
                MEASURE_READY = False
    client_socket.close()


def main():
    # Initialization
    i2c = I2C(0, I2C.MASTER, baudrate=100000)
    lps25hb = LPS25HB(i2c)

    # TODO: protocol choice
    protocol = 'WiFi'
    print('Protocol')
    if protocol == 'WiFi':
        print('WiFi')
        # Configure wifi in client mode
        wlan = WLAN(mode=WLAN.STA)
        wifi_client = WIFI_CLIENT(wlan, '192.168.4.1', 50000, )
        _thread.start_new_thread(lps25hb_thread, (lps25hb,))
        _thread.start_new_thread(wifi_client_thread, (wifi_client.client_socket,))
    elif protocol == 'Bluetooth':
        print('Bluetooth')
        pass


if __name__ == "__main__":
    main()
