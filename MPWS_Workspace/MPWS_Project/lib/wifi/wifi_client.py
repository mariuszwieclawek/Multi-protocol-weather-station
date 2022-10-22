from network import WLAN
import machine
import usocket
import _thread
import time
import pycom

SERVER_ADDRESS = '192.168.4.1'
SERVER_PORT = 50000

pycom.heartbeat(False)
# pycom.rgbled(0x7f0000) # red
# pycom.rgbled(0x00FF00)  # Green
pycom.rgbled(0x0000FF)  # Blue

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
pass
# while(True):
#     print('Wait for WiFi server response...')
#     data = client_socket.recv(100)
#     # If recv() returns with 0 the other end closed the connection
#     if len(data) == 0:
#         print('none received from server')
#         # clientsocket.close()
#     else:
#         # Do something with the received data...
#         print("Data received: " + str(data))
