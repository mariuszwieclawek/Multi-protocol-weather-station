from machine import I2C, Timer
from network import WLAN
import pycom
import _thread
import time
import ustruct
from wifi import WifiClient
from i2c_AM2320 import AM2320
from client import ClientData

pycom.heartbeat(False)
pycom.rgbled(0x7f0000) # Red


def main():
    # For saving measurement data and protocol choice
    client_data = ClientData()

    # Sensor which measure temperature and humidity
    am2320 = AM2320()

    # Configure wifi in client mode
    wifi_client = WifiClient(client_data)
    wifi_client.connect_to_wifi_server()
    wifi_client.connect_to_meas_socket()
    client_data.protocol = wifi_client.connect_to_proto_socket()

    am2320.start_measurement(client_data)

    while True:
        # When new protocol choice appear
        if client_data.protocol != client_data.protocol_buffer:
            if client_data.protocol == 'WiFi':
                client_data.protocol_buffer = 'WiFi'
                wifi_client.start_meas_thread(client_data)
                wifi_client.start_proto_thread(client_data)
            elif client_data.protocol == 'BLE':
                client_data.protocol_buffer = 'BLE'
                print('BLE')
                pass
            elif client_data.protocol == 'Sigfox':
                client_data.protocol_buffer = 'Sigfox'
                print('Sigfox')
                pass
            elif client_data.protocol == 'LTE-M':
                client_data.protocol_buffer = 'LTE-M'
                print('LTE-M')
                pass


if __name__ == "__main__":
    main()
