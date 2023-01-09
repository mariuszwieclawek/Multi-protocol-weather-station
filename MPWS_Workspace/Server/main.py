from machine import I2C
from network import WLAN
from network import LoRa
import pycom
import _thread
import time
import ustruct
import socket
from lora import LoraServer
from wifi import WifiServer
from ble import BleServer
from server import ServerData


def change_proto_thread(server_data):
    while True:
        time.sleep(10)
        server_data.protocol = 'BLE'
        time.sleep(10)
        server_data.protocol = 'WiFi'



def main():
    # Green LED
    pycom.heartbeat(False)
    pycom.rgbled(0x00FF00)

    # For saving measurement data and protocol choice
    server_data = ServerData()

    # Create server WiFi for handling data between Fipy and PC
    wifi_server = WifiServer()
    wifi_server.wifi_ap_init()

    # Create BLE server
    ble_server = BleServer()

    wifi_server.connect_to_pc_meas_socket()
    server_data.protocol = wifi_server.connect_to_pc_proto_socket()
    wifi_server.start_pc_proto_thread(server_data)
    wifi_server.start_pc_meas_thread(server_data)

    # LoRa server, for handling protocol choice between FiPy server and FiPy clients
    lora_server = LoraServer()
    lora_server.start_proto_handling_thread(server_data)
    lora_server.wait_for_client_get_proto()


    while True:
        print('\nProtocol chosen: ', server_data.protocol)
        if server_data.protocol == 'WiFi':
            # Connect with sensors. Start reading data from sensors and send them to pc client
            wifi_server.connect_with_sensors(server_data)
            wifi_server.start_am2320_meas_thread(server_data)
            wifi_server.start_lps25hb_meas_thread(server_data)
            while True:
                if server_data.protocol != 'WiFi': # When new protocol choice appear
                    lora_server.wait_for_client_get_proto()
                    break
        elif server_data.protocol == 'BLE':
            ble_server.start_ble_advertise(server_data)
            ble_server.register_am2320_meas_callbacks()
            ble_server.register_lps25hb_meas_callbacks()
            while True:
                if server_data.protocol != 'BLE':
                    lora_server.wait_for_client_get_proto()
                    break
        elif server_data.protocol == 'LoRa':
            print('LoRa')
            lora_server.start_meas_thread(server_data)
            while True:
                if server_data.protocol != 'LoRa':
                    lora_server.wait_for_client_get_proto()
                    break



if __name__ == "__main__":
    main()
