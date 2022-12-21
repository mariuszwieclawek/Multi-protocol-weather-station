import os
import socket
import time
import struct
from network import LoRa
import pycom

# Green LED
pycom.heartbeat(False)
pycom.rgbled(0x00FF00)

# A basic package header, B: 1 byte for the deviceId, B: 1 byte for the pkg size
_LORA_PKG_FORMAT = "BB%dsff"
_LORA_PKG_ACK_FORMAT = "BB%ds"
DEVICE_ID = 0x02


# Open a Lora Socket, use tx_iq to avoid listening to our own messages
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
lora = LoRa(mode=LoRa.LORA, tx_iq=True, region=LoRa.EU868)
lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
lora_sock.setblocking(False)

proto = 'LoRa'
TEMP = 21.4
PRESS = 1008.5
while(True):
    # Package send containing a simple string
    pkg = struct.pack(_LORA_PKG_FORMAT % len(proto), DEVICE_ID, len(proto), proto, TEMP, PRESS)
    lora_sock.send(pkg)
    # Wait for the response from the gateway. NOTE: For this demo the device does an infinite loop for while waiting the response. Introduce a max_time_waiting for you application
    recv_ack = lora_sock.recv(256)
    if (len(recv_ack) > 0):
        recv_pkg_len = recv_ack[1]
        try:
            device_id, proto_len, proto = struct.unpack(_LORA_PKG_ACK_FORMAT % recv_pkg_len, recv_ack)
        except:
            continue
        else:
            if (device_id == DEVICE_ID):
                print('Proto: ', proto)
    TEMP += 0.001
    PRESS += 0.001
    time.sleep(1)
