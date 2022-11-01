from network import WLAN
import machine
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
        # Accept maximum of 2 connections at the same time
        self.serversocket.listen(3)


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
