from machine import I2C, Timer
from network import WLAN
import pycom
import _thread
import time
import ustruct
from i2c_AM2320 import AM2320
from client import ClientData
from wifi import WifiClient
from ble import BleClientA


pycom.heartbeat(False)
pycom.rgbled(0x7f0000) # Red


def main():
    # For saving measurement data and protocol choice
    client_data = ClientData()

    # Sensor which measure temperature and humidity
    am2320 = AM2320()

    # Configure wifi in client mode and receive initial protocol choice
    wifi_client = WifiClient()
    wifi_client.connect_to_wifi_server()
    wifi_client.connect_to_meas_socket()
    client_data.protocol = wifi_client.connect_to_proto_socket()

    # BLE client
    ble_clt = BleClientA()

    # AM2320 start measurement
    am2320.start_measurement(client_data)

    TEST_FLAG = False
    while True:
        print('\nProtocol chosen: ', client_data.protocol)
        if client_data.protocol == 'WiFi':
            print('WESZLO DO WIFI')
            if TEST_FLAG == True:
                del wifi_client
                wifi_client = WifiClient()
                wifi_client.connect_to_wifi_server()
                wifi_client.connect_to_meas_socket()
                client_data.protocol = wifi_client.connect_to_proto_socket()
            wifi_client.start_meas_thread(client_data)
            wifi_client.start_proto_thread(client_data)
            while True:
                if client_data.protocol != 'WiFi':
                    break
        elif client_data.protocol == 'BLE':
            print('WESZLO DO BLE')
            TEST_FLAG = True
            while True:
                conn = ble_clt.connect_to_server(client_data)
                ble_clt.register_am2320_serv_and_char(conn)
                client_data.protocol = ble_clt.read_proto_value()
                if client_data.protocol != 'BLE': # stop thread
                    conn.disconnect()
                    break
                ble_clt.send_measurement_to_server(client_data)
                conn.disconnect()
                time.sleep(1)
        elif client_data.protocol == 'Sigfox':
            print('Sigfox')
            pass
        elif client_data.protocol == 'LTE-M':
            print('LTE-M')
            pass


if __name__ == "__main__":
    main()
