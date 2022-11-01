import socket
import struct


SERVER_ADDRESS = '192.168.4.1'
SERVER_PORT = 50000


def client_program():
    # Create a client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to server
    client_socket.connect(socket.getaddrinfo(SERVER_ADDRESS, SERVER_PORT)[0][-1])
    print('Connected to the server')
    client_socket.send(b'CLIENT_PC') # identify
    client_socket.send(b'WiFi') # protocol choice
    while True:
        data = client_socket.recv(16) # receive 4xfloat = 16bytes
        buff = struct.unpack('ffff', data)  # tuple with measurement values
        AM2320_HUMIDITY = buff[0]
        AM2320_TEMPERATURE = buff[1]
        LPS25HB_PRESSURE = buff[2]
        LPS25HB_TEMPERATURE = buff[3]
        print(f'AM2320_HUMIDITY: {AM2320_HUMIDITY}\nAM2320_TEMPERATURE: {AM2320_TEMPERATURE}\n'
              f'LPS25HB_PRESSURE: {LPS25HB_PRESSURE}\nLPS25HB_TEMPERATURE: {LPS25HB_TEMPERATURE}')
    client_socket.close()


if __name__ == '__main__':
    client_program()



