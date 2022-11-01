from network import WLAN
import usocket
import _thread
import time
import pycom

pycom.heartbeat(False)
pycom.rgbled(0x00FF00)  # Green

# Configure wifi in ap mode
wlan = WLAN(mode=WLAN.AP, ssid='WEATHER_STATION_AP', auth=(WLAN.WPA2,'weather123'), antenna=WLAN.INT_ANT, hidden=False)


# Thread for handling a client
def client_thread(clientsocket):
    print('Send some data to client')
    clientsocket.send('Welcome from server')
    print('Wait for WiFi client response...')
    data = clientsocket.recv(100) # receive data from server
    print('Data from client', data)
    clientsocket.close()

# Set up server socket
server_socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
server_socket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
server_socket.bind(("192.168.4.1", 50000))

# Accept maximum of 2 connections at the same time
server_socket.listen(2)

while True:
    # Accept the connection of the clients
    print('Wait for client')
    (client_socket, client_address) = server_socket.accept()
    print(type(client_address))
    print(type(client_address[0]))
    print(type(client_address[1]))
    print('Connection from: ', client_address)
    # Start a new thread to handle the client
    _thread.start_new_thread(client_thread, (client_socket,))
