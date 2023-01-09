from network import LoRa
import _thread
import time
import ustruct
import socket


class LoraServer:
    def __init__(self):
        self.lora = LoRa(mode=LoRa.LORA, rx_iq=True, region=LoRa.EU868)
        self.lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        self.lora_sock.setblocking(False)
        self.am_proto_ack = False
        self.lp_proto_ack = False
        self.proto_get_confirm = False


    def start_proto_handling_thread(self, server_data):
        _thread.start_new_thread(self.client_proto_thread, (server_data, self.lora_sock))


    def client_proto_thread(self, server_data, lora_sock):
        while True:
            # When new protocol choice send it to clients
            if server_data.protocol != server_data.protocol_buffer:
                server_data.protocol_buffer = server_data.protocol
                print('Send new protocol choice to the clients and wait for them response...')
                while self.am_proto_ack == False or self.lp_proto_ack == False:
                    lora_sock.send(server_data.protocol)
                    recv_ack = lora_sock.recv(64)
                    if (len(recv_ack) > 0):
                        device_id, ack = ustruct.unpack('BB', recv_ack)
                        if (device_id == 0x01):
                            if (ack == 200):
                                self.am_proto_ack = True
                                print("AM2320 PROTO ACK")
                        if (device_id == 0x02):
                            if (ack == 200):
                                self.lp_proto_ack = True
                                print("LPS25HB PROTO ACK")
                    time.sleep(1)
                self.am_proto_ack = False
                self.lp_proto_ack = False
                self.proto_get_confirm = True


    def wait_for_client_get_proto(self):
        while True:
            if self.proto_get_confirm == True:
                self.proto_get_confirm = False
                break
        print('! Clients got new protocol choice !')


    def start_meas_thread(self, server_data):
        _thread.start_new_thread(self.meas_thread, (server_data, self.lora_sock))


    def meas_thread(self, server_data, lora_sock):
        while (True):
            if server_data.protocol != 'LoRa': # stop thread
                break
            with server_data.lock:
                recv_data = lora_sock.recv(64)
                if (len(recv_data) > 2):
                    try:
                        device_id, value1, value2  = ustruct.unpack('Bff', recv_data)
                    except:
                        continue
                    else:
                        if device_id == 0x01:
                            server_data.AM2320_HUMIDITY = value1
                            server_data.AM2320_TEMPERATURE = value2
                            print('LoRa -> Humidity    - AM2320  = ', server_data.AM2320_HUMIDITY)
                            print('LoRa -> Temperature - AM2320  = ', server_data.AM2320_TEMPERATURE)
                        elif device_id == 0x02:
                            server_data.LPS25HB_PRESSURE = value1
                            server_data.LPS25HB_TEMPERATURE = value2
                            print('LoRa -> Pressure    - LPS25HB = ', server_data.LPS25HB_PRESSURE)
                            print('LoRa -> Temperature - LPS25HB = ', server_data.LPS25HB_TEMPERATURE)
        print('Thread stopped')
