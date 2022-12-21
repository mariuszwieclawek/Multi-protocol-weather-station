from network import LoRa
import socket
import time
import pycom
import _thread
import ustruct

pycom.heartbeat(False)
pycom.rgbled(0x0000FF)  # Blue

class LoraServer:
    def __init__(self):
        self.client_a_login = 'AM2320_CLIENT'
        self.client_b_login = 'LPS25HB_CLIENT'
        self.am2320_connection_success = False
        self.lps25hb_connection_success = False


    def lora_server_init(self):
        self.lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868)


    def wait_for_client_connection(self):
        (self.clientsocket, self.clientaddress) = self.serversocket.accept() # accept client connection
        print('New client connected - ', self.clientaddress)
        return self.clientsocket


    # Connect with client on PC (two sockets - one for measurement, second for protocol choice)
    def connect_to_pc_meas_socket(self):
        while True:
            # Wait for client connect
            print('Wait for PC Client...')
            self.client_pc_meas_socket = self.wait_for_client_connection()
            # Wait for client identification
            client_name = self.client_pc_meas_socket.recv(30).decode()
            if client_name == self.client_pc_login:
                self.client_pc_meas_socket.send('SUCCESS')
                print('CLIENT_PC connected') # CLIENT_PC connection
                break
            else:
                # unrecognised client connected
                print('Unrecognised client connected, close socket')
                self.client_pc_meas_socket.send('FAILURE')
                self.client_pc_meas_socket.close()


    def connect_to_pc_proto_socket(self):
        # Wait for protocol choice socket
        self.client_pc_proto_socket = self.wait_for_client_connection()
        # Initial protocol choice from PC
        print('Wait for protocol choice in PC Client...') # Protocol choice
        proto_choice = self.client_pc_proto_socket.recv(20).decode() # receive data from server
        return proto_choice


    def start_pc_proto_thread(self, server_data):
        _thread.start_new_thread(self.client_pc_proto_thread, (self.client_pc_proto_socket, server_data)) # Start pc client protocol choice thread


    def start_pc_meas_thread(self, server_data):
        _thread.start_new_thread(self.client_pc_meas_thread, (self.client_pc_meas_socket, server_data)) # Start pc client measurement thread

    # Thread for send measurement
    def client_pc_meas_thread(self, clientsocket, server_data):
        while True:
            with server_data.lock:
                if server_data.AM2320_HUMIDITY and server_data.AM2320_TEMPERATURE and server_data.LPS25HB_PRESSURE and server_data.LPS25HB_TEMPERATURE != 0: # wait for measurement after start program
                    data = ustruct.pack('ffff', server_data.AM2320_HUMIDITY, server_data.AM2320_TEMPERATURE, server_data.LPS25HB_PRESSURE, server_data.LPS25HB_TEMPERATURE)
                    clientsocket.send(data)
        clientsocket.close()


    # Thread for receive protocol choice
    def client_pc_proto_thread(self, clientsocket, server_data):
        while True:
            proto = clientsocket.recv(20).decode()
            if proto == 'WiFi' or 'BLE' or 'Sigfox' or 'LTE-M':
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
                # Wait for protocol choice socket
                self.client_am_proto_socket = self.wait_for_client_connection()
                print('Connected with protocol choice socket AM2320')
                self.client_am_proto_socket.send(server_data.protocol) # Initial choice
                print('Protocol choice send to AM2320: ', server_data.protocol)
            elif client_name == self.client_b_login:
                # LPS25HB_CLIENT client connection
                self.client_lp_meas_socket = self.sensor_socket
                self.client_lp_meas_socket.send('SUCCESS')
                print('LPS25HB_CLIENT connected')
                self.lps25hb_connection_success = True
                # Wait for protocol choice socket
                self.client_lp_proto_socket = self.wait_for_client_connection()
                print('Connected with protocol choice socket LPS25HB')
                self.client_lp_proto_socket.send(server_data.protocol) # Initial choice
                print('Protocol choice send to LPS25HB: ', server_data.protocol)
            else:
                # unrecognised client connected
                print('Unrecognised client connected, close socket')
                self.sensor_socket.send('FAILURE')
                self.sensor_socket.close()


    def start_am2320_meas_thread(self, server_data):
        _thread.start_new_thread(self.wifi_client_am2320_thread, (self.client_am_meas_socket, server_data))


    def start_lps25hb_meas_thread(self, server_data):
        _thread.start_new_thread(self.wifi_client_lps25hb_thread, (self.client_lp_meas_socket, server_data))


    # Start AM2320 client protocol choice thread
    def start_am2320_proto_thread(self, server_data):
        _thread.start_new_thread(self.wifi_client_am2320_proto_thread, (self.client_am_proto_socket, server_data))

    # Start LPS25HB client protocol choice thread
    def start_lps25hb_proto_thread(self, server_data):
        _thread.start_new_thread(self.wifi_client_lps25hb_proto_thread, (self.client_lp_proto_socket, server_data))

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


    # Thread for send protocol choice to the AM2320_CLIENT
    def wifi_client_am2320_proto_thread(self, am_proto_clientsocket, server_data):
        while True:
            if server_data.protocol != 'WiFi': # send new protocol and stop thread
                am_proto_clientsocket.send(server_data.protocol)
                print('WiFi: Send new protocol choice to AM2320')
                server_data.AM2320_HUMIDITY = 0
                server_data.AM2320_TEMPERATURE = 0
                break
        am_proto_clientsocket.close()


    # Thread for send protocol choice to the LPS25HB_CLIENT
    def wifi_client_lps25hb_proto_thread(self, lp_proto_clientsocket, server_data):
        while True:
            if server_data.protocol != 'WiFi': # send new protocol and stop thread
                lp_proto_clientsocket.send(server_data.protocol)
                print('WiFi: Send new protocol choice to LPS25HB')
                server_data.LPS25HB_PRESSURE = 0
                server_data.LPS25HB_TEMPERATURE = 0
                break
        lp_proto_clientsocket.close()


while True:
    data = s.recv(64)
    if data == b'Hello from client_A':
        print(data)
        s.send('Hello from server to client_A')
    elif data == b'Hello from client_B':
        print(data)
        s.send('Hello from server to client_B')
    time.sleep(1)
