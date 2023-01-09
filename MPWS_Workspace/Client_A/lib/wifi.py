from network import WLAN
import machine
import usocket
import _thread
import time
import pycom
import ustruct


class WifiClient:
    def __init__(self):
        self.login = 'AM2320_CLIENT'
        # Setup device as WiFi client
        self.wlan = WLAN(mode=WLAN.STA)
        self.server_address = '192.168.4.1'
        self.server_port = 50000


    def connect_to_wifi_server(self):
        self.wlan.connect(ssid='WEATHER_STATION_AP', auth=(WLAN.WPA2,'weather123'))
        print('Connecting to WiFi')
        while not self.wlan.isconnected():
            machine.idle()
        print("WiFi connected")


    def connect_to_meas_socket(self):
        # Create a client socket
        self.client_socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        # Connect to server
        while True:
            try:
                self.client_socket.connect(usocket.getaddrinfo(self.server_address, self.server_port)[0][-1])
            except OSError:
                continue
            else:
                break
        # Try to logging till the server is ready for setup connection
        self.client_socket.send(self.login) # Authenticate
        # Check if user logged or need wait for connection
        print('Wait for login to server...')
        login_status = self.client_socket.recv(20).decode() # wait for server response
        while True:
            print(login_status)
            if login_status == 'SUCCESS':
                break
            else:
                self.client_socket.close()
                self.client_socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
                self.client_socket.connect(usocket.getaddrinfo(self.server_address, self.server_port)[0][-1])
                self.client_socket.send(self.login) # Authenticate
            print('Wait for login to server...')
            login_status = self.client_socket.recv(20).decode() # wait for server response
            time.sleep(2)
        print('Connected to the server')


    def connect_to_proto_socket(self):
        # Connect to protocol choice socket
        self.client_proto_socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        self.client_proto_socket.connect(usocket.getaddrinfo(self.server_address, self.server_port)[0][-1])
        print('Wait for protocol choice...')
        proto = self.client_proto_socket.recv(20).decode() # Initial
        print('Protocol choice: ', proto)
        return proto


    def start_meas_thread(self, client_data):
        _thread.start_new_thread(self.client_meas_thread, (self.client_socket, client_data))


    # WiFi client measurement thread
    def client_meas_thread(self, meassocket, client_data):
        while True:
            if client_data.protocol != 'WiFi': # stop thread
                client_data.HUMIDITY = 0
                client_data.TEMPERATURE = 0
                break
            if client_data.MEASURE_READY == True:
                with client_data.lock:
                    print('Send humidity and temperature measurement to server')
                    try:
                        data = ustruct.pack('ff', client_data.HUMIDITY, client_data.TEMPERATURE)
                        meassocket.send(data)
                    except:
                        break
                    else:
                        client_data.MEASURE_READY = False
        meassocket.close()
