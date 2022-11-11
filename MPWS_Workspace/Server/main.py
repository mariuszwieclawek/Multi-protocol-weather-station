from machine import I2C
from network import WLAN
import pycom
import _thread
import time
import ustruct
from wifi import WIFI_SERVER
from wifi import WIFI_SERVER_CONTROLLER


def main():
    # Green LED
    pycom.heartbeat(False)
    pycom.rgbled(0x00FF00)

    # Create server WiFi
    wifi_server = WIFI_SERVER()

    # Create WiFi controller
    wifi_controller = WIFI_SERVER_CONTROLLER(wifi_server)
    wifi_controller.connect_with_pc()

    while True:
        if wifi_controller.PROTOCOL != wifi_controller.PROTOCOL_BUFFER:
            print('Protocol chosen: ', wifi_controller.PROTOCOL)
            if wifi_controller.PROTOCOL == 'WiFi':
                wifi_controller.PROTOCOL_BUFFER = 'WiFi'
                while True:
                    # Connect with sensors. Start reading data from sensors and send them to pc client
                    wifi_controller.connect_with_sensors()
                    # Check if sensors connected properly and exit infinity loop
                    if wifi_controller.am2320_connection_success == True and wifi_controller.lps25hb_connection_success == True:
                        wifi_controller.am2320_connection_success = False
                        wifi_controller.lps25hb_connection_success = False
                        break
            elif wifi_controller.PROTOCOL == 'BLE':
                wifi_controller.PROTOCOL_BUFFER = 'BLE'
                print('BLE')
                pass
            elif wifi_controller.PROTOCOL == 'Sigfox':
                wifi_controller.PROTOCOL_BUFFER = 'Sigfox'
                print('Sigfox')
                pass
            elif wifi_controller.PROTOCOL == 'LTE-M':
                wifi_controller.PROTOCOL_BUFFER = 'LTE-M'
                print('LTE-M')
                pass


if __name__ == "__main__":
    main()
