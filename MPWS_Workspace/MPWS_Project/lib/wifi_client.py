from network import WLAN
import machine
import usocket
import _thread
import time
import pycom

SERVER_ADDRESS = '192.168.4.1'
SERVER_PORT = 50000

pycom.heartbeat(False)
pycom.rgbled(0x0000FF)  # Blue

# WiFi client thread
def client_thread(clientsocket):
    print('Wait for WiFi server response...')
    data = clientsocket.recv(100) # receive data from server
    print('Data from server', data)
    print('Send back some data to server')
    clientsocket.send('Welcome from client')
    clientsocket.close()



# Setup device as WiFi client and connect to AP
wlan = WLAN(mode=WLAN.STA)
wlan.connect(ssid='WEATHER_STATION_AP', auth=(WLAN.WPA2,'weather123'))
print('Connecting to WiFi')
while not wlan.isconnected():
    machine.idle()
print("WiFi connected")

# Create a client socket
client_socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)

# Connect to server
client_socket.connect(usocket.getaddrinfo(SERVER_ADDRESS, SERVER_PORT)[0][-1])
print('Connected to the server')

# Start client thread
_thread.start_new_thread(client_thread, (client_socket,))
