from machine import I2C
from network import WLAN
import pycom
import _thread
from wifi import WIFI_CLIENT
from i2c_LPS25HB import LPS25HB

pycom.heartbeat(False)
pycom.rgbled(0x0000FF)  # Blue

# WiFi client thread
def client_thread(clientsocket):
    clientsocket.send('LPS25HB_CLIENT')
    while True:
        print('Wait for WiFi server response...')
        data = clientsocket.recv(20).decode()  # receive data from server
        print('Data from server:', data)
        print('Send back some data to server')
        clientsocket.send('Welcome from client')
        if str(data) == 'bye':
            break
    client_socket.close()


def main():
    protocol = 'WiFi'
    print('Protocol')
    if protocol == 'WiFi':
        print('WiFi')
        # Configure wifi in client mode
        wlan = WLAN(mode=WLAN.STA)
        wifi_client = WIFI_CLIENT(wlan, '192.168.4.1', 50000, )
        _thread.start_new_thread(client_thread, (wifi_client.client_socket,))
        pass
    elif protocol == 'Bluetooth':
        print('Bluetooth')
        pass


if __name__ == "__main__":
    main()
