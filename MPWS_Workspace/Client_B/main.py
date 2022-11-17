from machine import I2C, Timer
from network import WLAN
import pycom
import _thread
import time
import ustruct
from client import ClientData
from wifi import WifiClient
from ble import BleClientB
from i2c_LPS25HB import LPS25HB

pycom.heartbeat(False)
pycom.rgbled(0x0000FF)  # Blue


def main():
    # For saving measurement data and protocol choice
    client_data = ClientData()

    # Sensor which measure temperature and pressure
    lps25hb = LPS25HB()

    # Configure wifi in client mode
    wifi_client = WifiClient()
    wifi_client.connect_to_wifi_server()
    wifi_client.connect_to_meas_socket()
    client_data.protocol = wifi_client.connect_to_proto_socket()

    lps25hb.start_measurement(client_data)


    while True:
        # When new protocol choice appear
        if client_data.protocol != client_data.protocol_buffer:
            client_data.protocol_buffer = client_data.protocol
            if client_data.protocol == 'WiFi':
                wifi_client.start_meas_thread(client_data)
                wifi_client.start_proto_thread(client_data)
            elif client_data.protocol == 'BLE':
                print('BLE')
                ble_clt = BleClientB()
                while True:
                    if client_data.protocol != 'BLE': # stop thread
                        # kill object?
                        break
                    conn = ble_clt.connect_to_server(client_data)
                    ble_clt.register_lps25hb_serv_and_char(conn)
                    ble_clt.send_measurement_to_server(client_data)
                    ble_clt.send_proto_get_confirmation()
                    conn.disconnect()
                    time.sleep(3)
            elif client_data.protocol == 'Sigfox':
                print('Sigfox')
                pass
            elif client_data.protocol == 'LTE-M':
                print('LTE-M')
                pass


if __name__ == "__main__":
    main()
