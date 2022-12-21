import socket
import struct
import _thread
import time
from network import LoRa

class ServerData:
    def __init__(self):
        self.protocol = 'none'
        self.protocol_buffer = 'none'
        self.AM2320_HUMIDITY = 0
        self.AM2320_TEMPERATURE = 0
        self.LPS25HB_PRESSURE = 0
        self.LPS25HB_TEMPERATURE = 0
        self.lock = _thread.allocate_lock()

server_data = ServerData()

def change_proto_thread(server_data):
    while True:
        time.sleep(10)
        server_data.protocol = 'BLE'
        time.sleep(10)
        server_data.protocol = 'WiFi'

# for testing
_thread.start_new_thread(change_proto_thread, (server_data, ))
server_data.protocol = 'WiFi'
server_data.protocol_buffer = server_data.protocol
# end testing


# A basic package header, B: 1 byte for the deviceId, B: 1 byte for the pkg size, %ds: Formatted string for string
_LORA_PKG_FORMAT = "BB%dsff"
# A basic ack package, B: 1 byte for the deviceId, B: 1 byte for the pkg size, B: 1 byte for the Ok (200) or error messages
_LORA_PKG_ACK_FORMAT = "BB%ds"

lora = LoRa(mode=LoRa.LORA, rx_iq=True, region=LoRa.EU868)
lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
lora_sock.setblocking(True)

while (True):
    recv_data = lora_sock.recv(64)
    print(recv_data)
    if (len(recv_data) > 2):
        print(server_data.protocol)
        # pkg = struct.pack(_LORA_PKG_FORMAT % len(msg), DEVICE_ID, len(proto), proto, TEMP, HUM)
        recv_pkg_len = recv_data[1]
        device_id, proto_len, proto, value1, value2  = struct.unpack(_LORA_PKG_FORMAT % recv_pkg_len, recv_data)
        if device_id == 0x01:
            print('Device: %d - Proto:  %s - Temp: %f - Hum: %f' % (device_id, proto, value1, value2))
            ack_pkg = struct.pack(_LORA_PKG_ACK_FORMAT % recv_pkg_len, device_id, len(server_data.protocol), server_data.protocol)
            lora_sock.send(ack_pkg)
        elif device_id == 0x02:
            print('Device: %d - Proto:  %s - Temp: %f - Press: %f' % (device_id, proto, value1, value2))
            ack_pkg = struct.pack(_LORA_PKG_ACK_FORMAT % recv_pkg_len, device_id, len(server_data.protocol), server_data.protocol)
            lora_sock.send(ack_pkg)
