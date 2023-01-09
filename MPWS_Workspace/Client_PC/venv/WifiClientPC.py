import socket
import struct
import threading
import time


class ClientPC:
    def __init__(self):
        self.SERVER_ADDRESS = '192.168.4.1'
        self.SERVER_PORT = 50000
        self.login = b'CLIENT_PC_MEASUREMENT'


    # Connect to the Fipy Server. This function create two sockets. One for measurement, second for protocol choice
    # and connect do them. Fuction return list of measurement socket and protocol socket.
    def connect_to_server(self):
        # Create a measurement socket
        self.measurement_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # for measurement
        # Connect to server - measurement socket
        self.measurement_socket.connect(socket.getaddrinfo(self.SERVER_ADDRESS, self.SERVER_PORT)[0][-1])
        # Try to login to fipy server
        self.measurement_socket.send(self.login)  # identify
        print('Wait for login to server...')
        login_status = self.measurement_socket.recv(16).decode()  # receive if you logged properly
        while True:
            if login_status == 'SUCCESS':
                print('-> Logged properly to the server')
                # Create a proto choice socket
                self.protocol_choice_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # Connect to server - protocol choice socket
                self.protocol_choice_socket.connect(socket.getaddrinfo(self.SERVER_ADDRESS, self.SERVER_PORT)[0][-1])
                print('Connected to the server - protocol choice socket')
                break
            elif login_status == 'FAILURE':
                print('-> Failure logged to the server')
                self.measurement_socket.close()
                self.measurement_socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
                self.measurement_socket.connect(usocket.getaddrinfo(self.server_address, self.server_port)[0][-1])
                self.measurement_socket.send(self.login)  # Authenticate
            print('Wait for login to server...')
            login_status = self.measurement_socket.recv(20).decode()  # wait for server response
            time.sleep(2)
        return (self.measurement_socket, self.protocol_choice_socket)


    # Function start measurement thread
    def start_meas_thread(self, client_data):
        # Create thread for measurement
        self.meas_thread = threading.Thread(target=self.client_meas_thread, args=(self.measurement_socket, client_data))
        self.meas_thread.daemon = True  # Daemon threads are those threads which are killed when the main program exits.
        self.meas_thread.start()


    # Measurement thread
    def client_meas_thread(self, meas_socket, client_data):
        while True:
            with client_data.lock:
                try:
                    data = meas_socket.recv(16)  # receive 4xfloat = 16bytes
                    buff = struct.unpack('ffff', data)  # tuple with measurement values
                except:
                    continue
                else:
                    client_data.AM2320_HUMIDITY = buff[0]
                    client_data.AM2320_TEMPERATURE = buff[1]
                    client_data.LPS25HB_PRESSURE = buff[2]
                    client_data.LPS25HB_TEMPERATURE = buff[3]
                    print(f'AM2320_HUMIDITY: {client_data.AM2320_HUMIDITY}\nAM2320_TEMPERATURE: {client_data.AM2320_TEMPERATURE}\n'
                      f'LPS25HB_PRESSURE: {client_data.LPS25HB_PRESSURE}\nLPS25HB_TEMPERATURE: {client_data.LPS25HB_TEMPERATURE}')
        meas_socket.close()


