from machine import I2C
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

# LPS25HB sensor thread
def lps25hb_thread(lps25hb):
    global PRESSURE
    global TEMPERATURE
    while True:
        lock.acquire()
        PRESSURE = lps25hb.pressure_meas()
        TEMPERATURE = lps25hb.temperature_meas()
        print('Pressure: ', PRESSURE)
        print('Temperature: ', TEMPERATURE)
        lock.release()


# WiFi client thread
def wifi_client_thread(clientsocket):
    clientsocket.send('LPS25HB_CLIENT')
    while True:
        lock.acquire()
        print('Send pressure and temperature measurement to server')
        data = ustruct.pack('ff', PRESSURE, TEMPERATURE)
        clientsocket.send(data)
        lock.release()
    client_socket.close()


def main():
    # initialization
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
