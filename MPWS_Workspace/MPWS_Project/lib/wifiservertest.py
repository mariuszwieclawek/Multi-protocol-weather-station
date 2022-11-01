from network import WLAN
import usocket
import _thread
import time
import pycom


class WIFI_SERVER:
    def __init__(self, wlan):
        self.wlan = wlan
        # Set up server socket
        self.serversocket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        self.serversocket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
        self.serversocket.bind(("192.168.4.1", 50000))
        print('elo')


    def wait_for_client_response(self):
        print('elo')
        # Accept maximum of 2 connections at the same time
        self.serversocket.listen(2)
        # Accept the connection of the clients
        print('Wait for client')
        (self.clientsocket, self.clientaddress) = serversocket.accept()
        print('Client connected - ', self.clientaddress)
        # Start a new thread to handle the client
        _thread.start_new_thread(client_thread, (self.clientsocket,))


    def client_thread(clientsocket):
        # Sends back some data
        self.clientsocket.send(str('Welcome'))
        # Close the socket and terminate the thread
        self.clientsocket.close()


class WIFI_CLIENT:
    def __init__(self, wlan):
    self.SERVER_ADDRESS = '192.168.4.1'
    self.SERVER_PORT = 50000

    # Setup device as WiFi client and connect to AP
    self.wlan = wlan
    self.wlan.connect(ssid='WEATHER_STATION_AP', auth=(WLAN.WPA2,'weather123'))
    print('Connecting to WiFi')
    while not wlan.isconnected():
        machine.idle()
    print("WiFi connected")


    def connect_to_server(self, server_address, server_port):
        # Create a client socket
        client_socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        # Connect to server
        client_socket.connect(usocket.getaddrinfo(server_address, server_port)[0][-1])
        print('Connected to the server')


    # WiFi client thread
    def client_thread(clientsocket):
        while(True):
            print('Wait for WiFi server response...')
            data = clientsocket.recv(100) # receive data from server
            if len(data) > 0: #if we received data
                print("Data received from WiFi server: " + str(data))
            else:
                print('Nothing received from WiFi server')
                clientsocket.close()
                break




    # Start client thread
    _thread.start_new_thread(client_thread, (client_socket,))
    pass
