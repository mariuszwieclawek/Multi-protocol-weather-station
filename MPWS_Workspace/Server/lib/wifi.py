from network import WLAN
import machine
import usocket
import _thread
import time
import pycom
import ustruct


class WifiServer:
    def __init__(self):
        self.server_address = '192.168.4.1'
        self.server_port = 50000
        self.client_pc_login = 'CLIENT_PC_MEASUREMENT'
        self.client_a_login = 'AM2320_CLIENT'
        self.client_b_login = 'LPS25HB_CLIENT'
        self.am2320_connection_success = False
        self.lps25hb_connection_success = False


    def wifi_ap_init(self):
        # WLAN Access Point
        self.wlan = WLAN(mode=WLAN.AP, ssid='WEATHER_STATION_AP', auth=(WLAN.WPA2,'weather123'), antenna=WLAN.INT_ANT, hidden=False)
        # Set up server socket
        self.serversocket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        self.serversocket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
        self.serversocket.bind((self.server_address, self.server_port))
        # Accept maximum of 6 connections at the same time
        self.serversocket.listen(6)


    def wait_for_client_connection(self):
        (self.clientsocket, self.clientaddress) = self.serversocket.accept() # accept client connection
        print('New client connected - ', self.clientaddress)
        return self.clientsocket


    # Connect with client on PC on measurement socket
    def connect_to_pc_meas_socket(self):
        while True:
            # Wait for client connection
            print('Wait for PC Client...')
            self.client_pc_meas_socket = self.wait_for_client_connection()
            # Wait for client identification
            client_name = self.client_pc_meas_socket.recv(30).decode()
            if client_name == self.client_pc_login:
                self.client_pc_meas_socket.send('SUCCESS')
                print('-> CLIENT_PC connected') # CLIENT_PC connection
                break
            else:
                # unrecognised client connected
                print('-> Unrecognised client connected, close socket')
                self.client_pc_meas_socket.send('FAILURE')
                self.client_pc_meas_socket.close()


    def connect_to_pc_proto_socket(self):
        # Wait for protocol choice socket
        self.client_pc_proto_socket = self.wait_for_client_connection()
        # Initial protocol choice from PC
        print('Wait for protocol choice in PC Client...') # Protocol choice
        proto_choice = self.client_pc_proto_socket.recv(20).decode() # receive data from client
        print('-> Protocol choice: ', proto_choice)
        return proto_choice


    def start_pc_proto_thread(self, server_data):
        _thread.start_new_thread(self.client_pc_proto_thread, (self.client_pc_proto_socket, server_data)) # Start pc client protocol choice thread


    def start_pc_meas_thread(self, server_data):
        _thread.start_new_thread(self.client_pc_meas_thread, (self.client_pc_meas_socket, server_data)) # Start pc client measurement thread

    # Thread for send measurement
    def client_pc_meas_thread(self, clientsocket, server_data):
        while True:
            with server_data.lock:
                # wait for measurement after start program
                if server_data.AM2320_HUMIDITY and server_data.AM2320_TEMPERATURE and \
                    server_data.LPS25HB_PRESSURE and server_data.LPS25HB_TEMPERATURE != 0:
                    data = ustruct.pack('ffff', server_data.AM2320_HUMIDITY, server_data.AM2320_TEMPERATURE,\
                        server_data.LPS25HB_PRESSURE, server_data.LPS25HB_TEMPERATURE)
                    clientsocket.send(data)
        clientsocket.close()


    # Thread for receive protocol choice
    def client_pc_proto_thread(self, clientsocket, server_data):
        while True:
            proto = clientsocket.recv(20).decode()
            if proto == 'WiFi' or 'BLE' or 'LoRa':
                server_data.protocol = proto
                print('!!!!!!New protocol!!!!!!!!  :  ', server_data.protocol)
        clientsocket.close()


    # Connect with sensor stations (AM2320 and LPS25HB)
    def connect_with_sensors(self, server_data):
        while True:
            if self.am2320_connection_success == True and self.lps25hb_connection_success == True:
                self.am2320_connection_success = False
                self.lps25hb_connection_success = False
                break
            print('Wait for AM2320 / LPS25HB Client')
            self.sensor_socket = self.wait_for_client_connection()
            client_name = self.sensor_socket.recv(20).decode()
            if client_name == self.client_a_login:
                # AM2320_CLIENT client connection
                self.client_am_meas_socket = self.sensor_socket
                self.client_am_meas_socket.send('SUCCESS')
                print('AM2320_CLIENT connected')
                self.am2320_connection_success = True
            elif client_name == self.client_b_login:
                # LPS25HB_CLIENT client connection
                self.client_lp_meas_socket = self.sensor_socket
                self.client_lp_meas_socket.send('SUCCESS')
                print('LPS25HB_CLIENT connected')
                self.lps25hb_connection_success = True
            else:
                # unrecognised client connected
                print('Unrecognised client connected, close socket')
                self.sensor_socket.send('FAILURE')
                self.sensor_socket.close()


    def start_am2320_meas_thread(self, server_data):
        _thread.start_new_thread(self.wifi_client_am2320_thread, (self.client_am_meas_socket, server_data))


    def start_lps25hb_meas_thread(self, server_data):
        _thread.start_new_thread(self.wifi_client_lps25hb_thread, (self.client_lp_meas_socket, server_data))


    # Thread for receive sensor measurement AM2320
    def wifi_client_am2320_thread(self, sensorsocket, server_data):
        while True:
            if server_data.protocol != 'WiFi': # stop thread
                server_data.AM2320_HUMIDITY = 0
                server_data.AM2320_TEMPERATURE = 0
                break
            with server_data.lock:
                try:
                    data = sensorsocket.recv(8) # receive 2xfloat = 8bytes
                    buff = ustruct.unpack('ff', data) # tuple with measurement values
                except:
                    break
                else:
                    server_data.AM2320_HUMIDITY = buff[0]
                    server_data.AM2320_TEMPERATURE = buff[1]
                    print('WiFi -> Humidity    - AM2320  = ', server_data.AM2320_HUMIDITY)
                    print('WiFi -> Temperature - AM2320  = ', server_data.AM2320_TEMPERATURE)
        sensorsocket.close()


    # Thread for receive sensor measurement LPS25HB
    def wifi_client_lps25hb_thread(self, sensorsocket, server_data):
        while True:
            if server_data.protocol != 'WiFi': # stop thread
                server_data.LPS25HB_PRESSURE = 0
                server_data.LPS25HB_TEMPERATURE = 0
                break
            with server_data.lock:
                try:
                    data = sensorsocket.recv(8) # receive 2xfloat = 8bytes
                    buff = ustruct.unpack('ff', data) # tuple with measurement values
                except:
                    break
                else:
                    server_data.LPS25HB_PRESSURE = buff[0]
                    server_data.LPS25HB_TEMPERATURE = buff[1]
                    print('WiFi -> Pressure    - LPS25HB = ', server_data.LPS25HB_PRESSURE)
                    print('WiFi -> Temperature - LPS25HB = ', server_data.LPS25HB_TEMPERATURE)
        sensorsocket.close()
