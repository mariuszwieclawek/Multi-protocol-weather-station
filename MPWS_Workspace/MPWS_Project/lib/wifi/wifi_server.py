from network import WLAN
import usocket
import _thread
import time
import pycom

pycom.heartbeat(False)
# pycom.rgbled(0x7f0000) # red
pycom.rgbled(0x00FF00)  # Green
# pycom.rgbled(0x0000FF)  # Blue

# Configure wifi in ap mode
wlan = WLAN()
wlan.init(mode=WLAN.AP, ssid='WEATHER_STATION_AP', auth=(WLAN.WPA2,'weather123'), antenna=WLAN.INT_ANT, hidden=False)


# Thread for handling a client
def client_thread(clientsocket):
    # Sends back some data
    clientsocket.send(str('Welcome'))
    # Close the socket and terminate the thread
    clientsocket.close()

# Set up server socket
serversocket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
serversocket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
serversocket.bind(("192.168.4.1", 50000))

# Accept maximum of 2 connections at the same time
serversocket.listen(2)

while True:
    # Accept the connection of the clients
    print('Wait for client')
    (clientsocket, address) = serversocket.accept()
    # Start a new thread to handle the client
    _thread.start_new_thread(client_thread, (clientsocket,))
    