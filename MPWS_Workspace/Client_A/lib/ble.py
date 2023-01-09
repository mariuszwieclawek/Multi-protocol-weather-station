from network import Bluetooth
from machine import Timer
import pycom
import time
import ustruct


class BleClientA():
    def __init__(self):
        self.ble = Bluetooth()
        self.BLE_SERVER_NAME = 'WEATHER_STATION_BLE_SERVER'
        self.am2320_meas_service_uuid = 0x0010
        self.am2320_meas_serv_temp_char_uuid = 0x0100
        self.am2320_meas_serv_hum_char_uuid = 0x0101
        self.srv_am2320 = 0
        self.char_am_temp = 0
        self.char_am_hum = 0
        self.conn = 0


    def connect_to_server(self, client_data):
        print('Start scanning for BLE Server')
        self.ble.start_scan(-1)    # start scanning - no timeout
        while True:
            advert = self.ble.get_adv() # get advertisment from other bluetooth devices
            # when we get some adv need to check by name if it is FiPy Server.
            if advert and self.ble.resolve_adv_data(advert.data, Bluetooth.ADV_NAME_CMPL) == self.BLE_SERVER_NAME:
                try:
                    self.conn = self.ble.connect(advert.mac)
                except:
                    print('Connot connect')
                    self.ble.start_scan(-1) # start scanning again
                    continue
                else:
                    print('Connected to weather station')
                    self.ble.stop_scan()
                    return self.conn


    def register_am2320_serv_and_char(self, conn):
        services = conn.services() # service search for connected BLE server
        for service in services:
            service_uuid = service.uuid()
            if service_uuid == self.am2320_meas_service_uuid:
                self.srv_am2320 = service
                characteristics = service.characteristics()
                for char in characteristics:
                    char_uuid = char.uuid()
                    if char_uuid == self.am2320_meas_serv_temp_char_uuid: # char for send temperature
                        self.char_am_temp = char
                    elif char_uuid == self.am2320_meas_serv_hum_char_uuid: # char for send pressure
                        self.char_am_hum = char


    def send_measurement_to_server(self, client_data):
        temp = ustruct.pack('f', client_data.TEMPERATURE) # create bytes format
        hum = ustruct.pack('f', client_data.HUMIDITY) # create bytes format
        self.char_am_temp.write(temp)
        self.char_am_hum.write(hum)
