from machine import I2C
from network import WLAN
import pycom
import _thread
import time
import ustruct
from wifi import WifiServer
from ble import BleServer
from server import ServerData


def main():
    # Green LED
    pycom.heartbeat(False)
    pycom.rgbled(0x00FF00)

    # For saving measurement data and protocol choice
    server_data = ServerData()

    # Create server WiFi for handling data between Fipy and PC
    wifi_server = WifiServer(server_data)
    wifi_server.wifi_ap_init()

    wifi_server.connect_to_pc_meas_socket()
    server_data.protocol = wifi_server.connect_to_pc_proto_socket()
    wifi_server.start_pc_proto_thread(server_data)
    wifi_server.start_pc_meas_thread(server_data)

    # server_data.protocol = 'WiFi'
    while True:
        # When new protocol choice appear
        if server_data.protocol != server_data.protocol_buffer:
            server_data.protocol_buffer = server_data.protocol
            print('Protocol chosen: ', server_data.protocol)
            if server_data.protocol == 'WiFi':
                # Connect with sensors. Start reading data from sensors and send them to pc client
                wifi_server.connect_with_sensors()
                wifi_server.start_am2320_meas_thread(server_data)
                wifi_server.start_lps25hb_meas_thread(server_data)
                wifi_server.start_am2320_proto_thread(server_data)
                wifi_server.start_lps25hb_proto_thread(server_data)
                print('WiFi')
            elif server_data.protocol == 'BLE':
                ble_server = BleServer()
                ble_server.start_ble_advertise()
                ble_server.start_new_proto_choice_thread(server_data)
                print('BLE')
            elif server_data.protocol == 'Sigfox':
                print('Sigfox')
                pass
            elif server_data.protocol == 'LTE-M':
                print('LTE-M')
                pass


if __name__ == "__main__":
    main()
