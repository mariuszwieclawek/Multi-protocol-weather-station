from network import WLAN
import machine
import usocket
import _thread
import time
import pycom
import ustruct


class WIFI_SERVER:
    def __init__(self):
        self.wlan = WLAN(mode=WLAN.AP, ssid='WEATHER_STATION_AP', auth=(WLAN.WPA2,'weather123'), antenna=WLAN.INT_ANT, hidden=False)
        # Set up server socket
        self.serversocket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        self.serversocket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
        self.serversocket.bind(("192.168.4.1", 50000))
        # Accept maximum of 4 connections at the same time
        self.serversocket.listen(4)


    def wait_for_client_connection(self):
        (self.clientsocket, self.clientaddress) = self.serversocket.accept() # accept client connection
        print('New client connected - ', self.clientaddress)
        return self.clientsocket


class WIFI_CLIENT:
    def __init__(self, wlan, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port

        # Setup device as WiFi client and connect to AP
        self.wlan = wlan
        self.wlan.connect(ssid='WEATHER_STATION_AP', auth=(WLAN.WPA2,'weather123'))
        print('Connecting to WiFi')
        while not wlan.isconnected():
            machine.idle()
        print("WiFi connected")

        # Create a client socket
        self.client_socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        # Connect to server
        self.client_socket.connect(usocket.getaddrinfo(self.server_address, self.server_port)[0][-1])
        print('Connected to the server')


class WIFI_SERVER_CONTROLLER:
    def __init__(self, wifi_server):
        self.wifi_server = wifi_server
        self.PROTOCOL = 'none'
        self.PROTOCOL_BUFFER = 'none'
        self.AM2320_HUMIDITY = 0
        self.AM2320_TEMPERATURE = 0
        self.LPS25HB_PRESSURE = 0
        self.LPS25HB_TEMPERATURE = 0
        self.client_pc_login = 'CLIENT_PC_MEASUREMENT'
        self.client_a_login = 'AM2320_CLIENT'
        self.client_b_login = 'LPS25HB_CLIENT'
        self.lock = _thread.allocate_lock()
        self.am2320_connection_success = False
        self.lps25hb_connection_success = False


    # Thread for send measurement
    def client_pc_meas_thread(self, clientsocket):
        while True:
            with self.lock:
                if self.AM2320_HUMIDITY and self.AM2320_TEMPERATURE and self.LPS25HB_PRESSURE and self.LPS25HB_TEMPERATURE != 0: # wait for measurement after start program
                    data = ustruct.pack('ffff', self.AM2320_HUMIDITY, self.AM2320_TEMPERATURE, self.LPS25HB_PRESSURE, self.LPS25HB_TEMPERATURE)
                    clientsocket.send(data)
        clientsocket.close()


    # Thread for receive protocol choice
    def client_pc_proto_thread(self, clientsocket):
        while True:
            self.PROTOCOL = clientsocket.recv(20).decode()
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!New protocol:', self.PROTOCOL)
        clientsocket.close()


    # Connect with client on PC (two sockets - one for measurement, second for protocol choice)
    def connect_with_pc(self):
        while True:
            # Wait for client connect
            print('Wait for PC Client...')
            self.client_pc_meas_socket = self.wifi_server.wait_for_client_connection()
            # Wait for client identification
            client_name = self.client_pc_meas_socket.recv(30).decode()
            if client_name == self.client_pc_login:
                print('CLIENT_PC connected') # CLIENT_PC connection
                _thread.start_new_thread(self.client_pc_meas_thread, (self.client_pc_meas_socket,)) # Start pc client measurement thread
                # Wait for protocol choice socket
                self.client_pc_proto_socket = self.wifi_server.wait_for_client_connection()
                # Initial protocol choice from PC
                print('Wait for protocol choice in PC Client...') # Protocol choice
                self.PROTOCOL = self.client_pc_proto_socket.recv(20).decode() # receive data from server
                _thread.start_new_thread(self.client_pc_proto_thread, (self.client_pc_proto_socket,)) # Start pc client protocol choice thread
                break
            else:
                # unrecognised client connected
                print('Unrecognised client connected, close socket')
                self.client_pc_meas_socket.close()


    # Thread for receive sensor measurement AM2320
    def wifi_client_am2320_thread(self, sensorsocket):
        while True:
            with self.lock:
                print('Wait for AM2320 measurement...')
                data = sensorsocket.recv(8) # receive 2xfloat = 8bytes
                buff = ustruct.unpack('ff', data) # tuple with measurement values
                self.AM2320_HUMIDITY = buff[0]
                self.AM2320_TEMPERATURE = buff[1]
                print('Humidity: ', self.AM2320_HUMIDITY)
                print('Temperature: ', self.AM2320_TEMPERATURE)
            if self.PROTOCOL != 'WiFi': # stop thread
                self.AM2320_HUMIDITY = 0
                self.AM2320_TEMPERATURE = 0
                sensorsocket.close()
                break


    # Thread for receive sensor measurement LPS25HB
    def wifi_client_lps25hb_thread(self, sensorsocket):
        while True:
            with self.lock:
                print('Wait for LPS25HB measurement...')
                data = sensorsocket.read(8) # receive 2xfloat = 8bytes
                buff = ustruct.unpack('ff', data) # tuple with measurement values
                self.LPS25HB_PRESSURE = buff[0]
                self.LPS25HB_TEMPERATURE = buff[1]
                print('Pressure: ', self.LPS25HB_PRESSURE)
                print('Temperature: ', self.LPS25HB_TEMPERATURE)
            if self.PROTOCOL != 'WiFi': # stop thread
                self.LPS25HB_PRESSURE = 0
                self.LPS25HB_TEMPERATURE = 0
                sensorsocket.close()
                break


    # Connect with sensor stations (AM2320 and LPS25HB)
    def connect_with_sensors(self):
        print('Wait for AM2320 / LPS25HB Client')
        self.sensor_socket = self.wifi_server.wait_for_client_connection()
        client_name = self.sensor_socket.recv(20).decode()
        if client_name == self.client_a_login:
            # AM2320_CLIENT client connection
            print('AM2320_CLIENT connected')
            self.am2320_connection_success = True
            _thread.start_new_thread(self.wifi_client_am2320_thread, (self.sensor_socket,))
        elif client_name == self.client_b_login:
            # LPS25HB_CLIENT client connection
            print('LPS25HB_CLIENT connected')
            self.lps25hb_connection_success = True
            _thread.start_new_thread(self.wifi_client_lps25hb_thread, (self.sensor_socket,))
        else:
            # unrecognised client connected
            print('Unrecognised client connected, close socket')
            self.sensor_socket.close()
