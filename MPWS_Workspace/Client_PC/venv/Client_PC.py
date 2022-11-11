import socket
import struct
import threading
import time


class PC_CLIENT:
    def __init__(self):
        self.SERVER_ADDRESS = '192.168.4.1'
        self.SERVER_PORT = 50000
        self.AM2320_HUMIDITY = 0
        self.AM2320_TEMPERATURE = 0
        self.LPS25HB_PRESSURE = 0
        self.LPS25HB_TEMPERATURE = 0
        # Create a measurement socket
        self.measurement_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # for measurement
        # Connect to server - measurement socket
        self.measurement_socket.connect(socket.getaddrinfo(self.SERVER_ADDRESS, self.SERVER_PORT)[0][-1])
        print('Connected to the server - measurement socket')
        self.measurement_socket.send(b'CLIENT_PC_MEASUREMENT')  # identify
        # Create thread for measurement
        self.meas_thread = threading.Thread(target=self.client_meas_thread, args=(self.measurement_socket,))
        self.meas_thread.daemon = True  # Daemon threads are those threads which are killed when the main program exits.
        self.meas_thread.start()


    def client_meas_thread(self, meas_socket):
        while True:
            data = meas_socket.recv(16)  # receive 4xfloat = 16bytes
            buff = struct.unpack('ffff', data)  # tuple with measurement values
            self.AM2320_HUMIDITY = buff[0]
            self.AM2320_TEMPERATURE = buff[1]
            self.LPS25HB_PRESSURE = buff[2]
            self.LPS25HB_TEMPERATURE = buff[3]
            print(f'AM2320_HUMIDITY: {self.AM2320_HUMIDITY}\nAM2320_TEMPERATURE: {self.AM2320_TEMPERATURE}\n'
              f'LPS25HB_PRESSURE: {self.LPS25HB_PRESSURE}\nLPS25HB_TEMPERATURE: {self.LPS25HB_TEMPERATURE}')
        meas_socket.close()


