from machine import I2C
from network import WLAN
import pycom
import _thread
import time
import ustruct
from wifi import WIFI_SERVER


lock = _thread.allocate_lock()


def client_pc_thread(clientsocket):
    while True:
        lock.acquire()
        try:
            data = ustruct.pack('ffff', AM2320_HUMIDITY, AM2320_TEMPERATURE, LPS25HB_PRESSURE, LPS25HB_TEMPERATURE)
            clientsocket.send(data)
        except NameError:
            pass
        lock.release()
    clientsocket.close()


def client_am2320_thread(clientsocket):
    global AM2320_HUMIDITY
    global AM2320_TEMPERATURE
    while True:
        lock.acquire()
        print('Wait for AM2320 measurement...')
        data = clientsocket.recv(8) # receive 2xfloat = 8bytes
        buff = ustruct.unpack('ff', data) # tuple with measurement values
        AM2320_HUMIDITY = buff[0]
        AM2320_TEMPERATURE = buff[1]
        print('Humidity: ', AM2320_HUMIDITY)
        print('Temperature: ', AM2320_TEMPERATURE)
        lock.release()
    clientsocket.close()


def client_lps25hb_thread(clientsocket):
    global LPS25HB_PRESSURE
    global LPS25HB_TEMPERATURE
    while True:
        lock.acquire()
        print('Wait for LPS25HB measurement...')
        data = clientsocket.read(8) # receive 2xfloat = 8bytes
        buff = ustruct.unpack('ff', data) # tuple with measurement values
        LPS25HB_PRESSURE = buff[0]
        LPS25HB_TEMPERATURE = buff[1]
        print('Pressure: ', LPS25HB_PRESSURE)
        print('Temperature: ', LPS25HB_TEMPERATURE)
        lock.release()
    clientsocket.close()


def main():
    # Green LED
    pycom.heartbeat(False)
    pycom.rgbled(0x00FF00)

    # Configure wifi in ap mode
    wlan = WLAN(mode=WLAN.AP, ssid='WEATHER_STATION_AP', auth=(WLAN.WPA2,'weather123'), antenna=WLAN.INT_ANT, hidden=False)
    wifi_server = WIFI_SERVER(wlan)

    # Connect with client on PC
    while True:
        # Wait for client connect
        print('Wait for PC Client...')
        client_pc_socket = wifi_server.wait_for_client_connection()
        # Wait for client identification
        client_name = client_pc_socket.recv(20).decode()
        if str(client_name) == 'CLIENT_PC':
            # CLIENT_PC connection
            print('CLIENT_PC connected')
            # Protocol choice
            print('Wait for protocol choice in PC Client...')
            global PROTOCOL
            PROTOCOL = client_pc_socket.recv(20).decode() # receive data from server
            print('Protocol choice: ', str(PROTOCOL))
            # Start pc client thread
            _thread.start_new_thread(client_pc_thread, (client_pc_socket,))
            break
        else:
            # unrecognised client connected
            print('Unrecognised client connected, close socket')
            client_pc_socket.close()

    # PROTOCOL = 'WiFi'
    # print(str(PROTOCOL))
    if str(PROTOCOL) == 'WiFi':
        while True:
            print('Wait for AM2320 / LPS25HB Client')
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
    elif PROTOCOL == 'Bluetooth':
        print('Bluetooth')
        pass


if __name__ == "__main__":
    main()
