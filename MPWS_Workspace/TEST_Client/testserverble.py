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

# A basic package header, B: 1 byte for the deviceId, B: 1 byte for the pkg size, %ds: Formatted string for string
_LORA_PKG_FORMAT = "BB%dsff"

def change_proto_thread(server_data, lora_sock):
    while True:
        time.sleep(10)
        print('!!!!!!! NEW PROTO !!!!! : BLE')
        server_data.protocol = 'BLE'
        lora_sock.send('BLE')
        time.sleep(10)
        print('!!!!!!! NEW PROTO !!!!! : WiFi')
        server_data.protocol = 'WiFi'
        lora_sock.send('WiFi')
        time.sleep(10)
        print('!!!!!!! NEW PROTO !!!!! : LoRa')
        server_data.protocol = 'LoRa'
        lora_sock.send('LoRa')

lora = LoRa(mode=LoRa.LORA, rx_iq=True, region=LoRa.EU868)
lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
lora_sock.setblocking(True)

# for testing
_thread.start_new_thread(change_proto_thread, (server_data, lora_sock))
server_data.protocol = 'WiFi'
server_data.protocol_buffer = server_data.protocol
# end testing

while (True):
    recv_data = lora_sock.recv(64)
    if (len(recv_data) > 2):
        print(server_data.protocol)
        recv_pkg_len = recv_data[1]
        try:
            device_id, proto_len, proto, value1, value2  = struct.unpack(_LORA_PKG_FORMAT % recv_pkg_len, recv_data)
        except:
            continue
        else:
            if device_id == 0x01:
                print('Device: %d - Proto:  %s - Temp: %f - Hum: %f' % (device_id, proto, value1, value2))
            elif device_id == 0x02:
                print('Device: %d - Proto:  %s - Temp: %f - Press: %f' % (device_id, proto, value1, value2))
