from network import LoRa
import socket
import machine
import time
import ustruct

lora = LoRa(mode=LoRa.LORA, tx_iq=True, region=LoRa.EU868)
lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
lora_sock.setblocking(False)

test = 'none'

def wait_for_start_request(lora_sock):
    print('czekamy na start_Req')
    while True:
        start_req = lora_sock.recv(64).decode()
        if len(start_req) > 0:
            print(start_req)
            if start_req == 'START':
                time.sleep_ms(20)
                lora_sock.send('START_ACK')
                break
        pass

while(True):
    data_recv = lora_sock.recv(64).decode()
    if (len(data_recv) > 0):
        print('Odebrano: ', data_recv)
        # print(client_data.protocol_buffer)
        # print(client_data.protocol)
        if data_recv == 'WiFi' or data_recv == 'BLE' or data_recv == 'LoRa':
            # if client_data.protocol != data_recv:
            if test != data_recv:
                print('wysłano ack')
                test = data_recv
                proto_ack = ustruct.pack('BB', 0x02, 200)
                lora_sock.send(proto_ack)
                wait_for_start_request(lora_sock)
                break
