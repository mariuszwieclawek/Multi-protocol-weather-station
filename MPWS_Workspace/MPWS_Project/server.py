from machine import I2C
from network import WLAN
import pycom
import _thread
from wifi import WIFI_SERVER

pycom.heartbeat(False)
pycom.rgbled(0x00FF00)  # Green led


def client_pc_thread(clientsocket):
    lock = _thread.allocate_lock()
    while True:
        lock.acquire()
        print('Send some data to client')
        clientsocket.send('Welcome from server')
        print('Wait for WiFi client response...')
        data = clientsocket.recv(100) # receive data from server
        print('Data from client', data)
        if str(data) == 'bye':
            break
        lock.release()
    clientsocket.close()


def client_am2320_thread(clientsocket):
    lock = _thread.allocate_lock()
    while True:
        lock.acquire()
        print('Wait for WiFi client send measurement')
        humidity = clientsocket.recv(20) # receive data from server
        temperature = clientsocket.recv(20)
        print('Humidity: ', humidity)
        print('Temperature: ', temperature)
        lock.release()
    clientsocket.close()


def client_lps25hb_thread(clientsocket):
    lock = _thread.allocate_lock()
    while True:
        lock.acquire()
        print('Wait for WiFi client send measurement')
        pressure = clientsocket.recv(20) # receive data from server
        temperature = clientsocket.recv(20)
        print('Pressure: ', pressure)
        print('Temperature: ', temperature)
        lock.release()
    clientsocket.close()


def main():
    # Configure wifi in ap mode
    wlan = WLAN(mode=WLAN.AP, ssid='WEATHER_STATION_AP', auth=(WLAN.WPA2,'weather123'), antenna=WLAN.INT_ANT, hidden=False)
    wifi_server = WIFI_SERVER(wlan)

    # # Connect with client on PC
    # while True:
    #     # Wait for client connect
    #     client_socket = wifi_server.wait_for_client_connection()
    #     # Wait for client identification
    #     client_name = client_socket.recv(20).decode()
    #     if str(client_name) == 'CLIENT_PC':
    #         # CLIENT_PC connection
    #         print('CLIENT_PC connected')
    #         _thread.start_new_thread(client_pc_thread, (client_socket,))
    #         break
    #     else:
    #         # unrecognised client connected
    #         print('Unrecognised client connected, close socket')
    #         client_socket.close()

    # TODO: implement protocol choice
    protocol = 'WiFi'
    print('Protocol choice: ', protocol)
    if protocol == 'WiFi':
        while True:
            client_socket = wifi_server.wait_for_client_connection()
            client_name = client_socket.recv(20).decode()
            if str(client_name) == 'AM2320_CLIENT':
                # AM2320_CLIENT client connection
                print('AM2320_CLIENT connected')
                _thread.start_new_thread(client_am2320_thread, (client_socket,))
            elif str(client_name) == 'LPS25HB_CLIENT':
                # LPS25HB_CLIENT client connection
                print('LPS25HB_CLIENT connected')
                _thread.start_new_thread(client_lps25hb_thread, (client_socket,))
            else:
                # unrecognised client connected
                print('Unrecognised client connected, close socket')
                client_socket.close()
    elif protocol == 'Bluetooth':
        print('Bluetooth')
        pass


if __name__ == "__main__":
    main()
