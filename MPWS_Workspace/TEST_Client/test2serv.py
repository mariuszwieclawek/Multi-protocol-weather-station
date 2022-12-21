from network import LoRa
import socket
import machine
import time
import ustruct

lora = LoRa(mode=LoRa.LORA, rx_iq=True, region=LoRa.EU868)
lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
lora_sock.setblocking(False)
am_proto_ack = False
lp_proto_ack = False

def wait_for_start_ack(lora_sock):
    lora_sock.send('START')
    print('czekamy na start ack')
    while True:
        start_ack = lora_sock.recv(64).decode()
        if len(start_ack) > 0:
            print(start_ack)
            if start_ack == 'START_ACK':
                break
        time.sleep_ms(20)
        lora_sock.send('START')
    print('START TRANSMISSION')

while True:
    # When new protocol choice send it to clients
    # if server_data.protocol != server_data.protocol_buffer:
    #     server_data.protocol_buffer = server_data.protocol
    print('Send new protocol choice to the clients and wait for them response...')
    # self.am_proto_ack = False
    # self.lp_proto_ack = False
    am_proto_ack = False
    lp_proto_ack = False
    # while self.am_proto_ack == False or self.lp_proto_ack == False:
    while am_proto_ack == False or lp_proto_ack == False:
        # lora_sock.send(server_data.protocol)
        lora_sock.send('WiFi')
        proto_ack = lora_sock.recv(64)
        if (len(proto_ack) > 0):
            device_id, ack = ustruct.unpack('BB', proto_ack)
            if (device_id == 0x01):
                if (ack == 200):
                    # self.am_proto_ack = True
                    am_proto_ack = True
                    print("AM2320 PROTO ACK")
                    time.sleep_ms(20)
                    wait_for_start_ack(lora_sock)
            if (device_id == 0x02):
                if (ack == 200):
                    lp_proto_ack = True
                    lp_proto_ack = True
                    print("LPS25HB PROTO ACK")
                    time.sleep_ms(20)
                    wait_for_start_ack(lora_sock)
        time.sleep(1)
