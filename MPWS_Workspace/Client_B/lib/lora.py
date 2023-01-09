from network import LoRa
import _thread
import time
import ustruct
import socket
import machine


class LoraClientB:
    def __init__(self):
        self.lora = LoRa(mode=LoRa.LORA, tx_iq=True, region=LoRa.EU868)
        self.lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        self.lora_sock.setblocking(False)


    def start_proto_handling_thread(self, client_data):
        _thread.start_new_thread(self.proto_handling_thread, (client_data, self.lora_sock))


    def proto_handling_thread(self, client_data, lora_sock):
        proto_ack = ustruct.pack('BB', 0x02, 200)
        while(True):
            data_recv = lora_sock.recv(64).decode()
            if (len(data_recv) > 0):
                print('Odebrano: ', data_recv)
                if data_recv == 'WiFi' or data_recv == 'BLE' or data_recv == 'LoRa':
                    lora_sock.send(proto_ack)
                    print('wysłano ack')
                    client_data.protocol = data_recv
            time.sleep(1)


    def wait_for_get_proto(self, client_data):
        print('Wait for protocol choice...')
        while client_data.protocol == 'none':
            continue
        print('-> Protocol choice: ', client_data.protocol)


    def start_meas_thread(self, client_data):
        _thread.start_new_thread(self.meas_thread, (client_data, self.lora_sock))


    def meas_thread(self, client_data, lora_sock):
        while True:
            if client_data.protocol != 'LoRa': # stop thread
                break
            pkg = ustruct.pack('Bff', 0x02, client_data.PRESSURE, client_data.TEMPERATURE)
            lora_sock.send(pkg)
            time.sleep(1)
        print('Thread stopped')
