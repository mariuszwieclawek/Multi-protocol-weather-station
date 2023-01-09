from machine import I2C, Timer
from network import WLAN
from network import LoRa
import pycom
import _thread
import time
import ustruct
import socket
from i2c_LPS25HB import LPS25HB
from client import ClientData
from wifi import WifiClient
from ble import BleClientB
from lora import LoraClientB


pycom.heartbeat(False)
pycom.rgbled(0x0000FF)  # Blue


def main():
    # For saving measurement data and protocol choice
    client_data = ClientData()

    # Sensor which measure temperature and pressure
    lps25hb = LPS25HB()

    # LPS25HB start measurement
    lps25hb.start_measurement(client_data)

    # LoRa client, start protocol choice handling thread
    lora_client = LoraClientB()
    lora_client.start_proto_handling_thread(client_data)
    lora_client.wait_for_get_proto(client_data)

    # BLE client
    ble_clt = BleClientB()

    # WiFi clients
    wifi_client = WifiClient()

    while True:
        print('\nProtocol chosen: ', client_data.protocol)
        if client_data.protocol == 'WiFi':
            wifi_client.connect_to_wifi_server()
            wifi_client.connect_to_meas_socket()
            wifi_client.start_meas_thread(client_data)
            while True:
                if client_data.protocol != 'WiFi':
                    break
        elif client_data.protocol == 'BLE':
            while True:
                conn = ble_clt.connect_to_server(client_data)
                ble_clt.register_lps25hb_serv_and_char(conn)
                if client_data.protocol != 'BLE': # stop thread
                    conn.disconnect()
                    break
                ble_clt.send_measurement_to_server(client_data)
                conn.disconnect()
                time.sleep(1)
        elif client_data.protocol == 'LoRa':
            print('LoRa')
            lora_client.start_meas_thread(client_data)
            while True:
                if client_data.protocol != 'LoRa':
                    break


if __name__ == "__main__":
    main()
