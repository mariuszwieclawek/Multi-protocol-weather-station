import os
import socket
import time
import struct
from network import LoRa
import pycom

pycom.heartbeat(False)
pycom.rgbled(0x7f0000) # Red

# A basic package header, B: 1 byte for the deviceId, B: 1 byte for the pkg size
_LORA_PKG_FORMAT = "BB%dsff"
DEVICE_ID = 0x01

lora = LoRa(mode=LoRa.LORA, tx_iq=True, region=LoRa.EU868)
lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
lora_sock.setblocking(False)

proto = 'none'
TEMP = 21.4
HUM = 68.5
print('HelloClientA')
while(True):
    # Package send containing a simple string
    pkg = struct.pack(_LORA_PKG_FORMAT % len(proto), DEVICE_ID, len(proto), proto, TEMP, HUM)
    lora_sock.send(pkg)
    # Wait for the response from the gateway. NOTE: For this demo the device does an infinite loop for while waiting the response. Introduce a max_time_waiting for you application
    proto_choice = lora_sock.recv(64).decode()
    if (len(proto_choice) > 0):
        print(proto_choice)
        if proto_choice == 'WiFi':
            proto = 'WiFi'
        elif proto_choice == 'BLE':
            proto = 'BLE'
        elif proto_choice == 'LoRa':
            proto = 'LoRa'
    TEMP += 0.001
    HUM += 0.001
    time.sleep(1)
