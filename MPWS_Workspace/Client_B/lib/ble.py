from network import Bluetooth
from machine import Timer
import pycom
import time
import ustruct


class BleClientB():
    def __init__(self):
        self.ble = Bluetooth()
        self.BLE_SERVER_NAME = 'WEATHER_STATION_BLE_SERVER'
        self.lps25hb_meas_service_uuid = 0x0020
        # self.lps25hb_prot_service_uuid = 0x0021
        self.lps25hb_meas_serv_temp_char_uuid = 0x0200
        self.lps25hb_meas_serv_press_char_uuid = 0x0201
        # self.lps25hb_prot_serv_char_uuid = 0x0250
        self.srv_lps25hb = 0
        # self.srv_lps25hb_proto = 0
        self.char_lp_temp = 0
        self.char_lp_press = 0
        # self.char_lp_proto = 0
        self.conn = 0
        # self.proto_choice_get = False


    def connect_to_server(self, client_data):
        self.client_data = client_data
        print('Start scanning for BLE Server')
        self.ble.start_scan(-1)    # start scanning - no timeout
        while True:
            advert = self.ble.get_adv() # get advertisment from other bluetooth devices
            if advert and self.ble.resolve_adv_data(advert.data, Bluetooth.ADV_NAME_CMPL) == self.BLE_SERVER_NAME: #check if it is our weather station: # when we get some adv
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


    def register_lps25hb_serv_and_char(self, conn):
        services = conn.services() # service search for connected BLE server
        for service in services:
            service_uuid = service.uuid()
            if service_uuid == self.lps25hb_meas_service_uuid:
                self.srv_lps25hb = service
                characteristics = service.characteristics()
                for char in characteristics:
                    char_uuid = char.uuid()
                    if char_uuid == self.lps25hb_meas_serv_temp_char_uuid: # char for send temperature
                        self.char_lp_temp = char
                    elif char_uuid == self.lps25hb_meas_serv_press_char_uuid: # char for send pressure
                        self.char_lp_press = char
            # elif service_uuid == self.lps25hb_prot_service_uuid:
            #     self.srv_lps25hb_proto = service
            #     characteristics = service.characteristics()
            #     for char in characteristics:
            #         char_uuid = char.uuid()
            #         if char_uuid == self.lps25hb_prot_serv_char_uuid: # char for proto choice receive
            #             self.char_lp_proto = char


    def send_measurement_to_server(self, client_data):
        temp = ustruct.pack('f', client_data.TEMPERATURE) # create bytes format
        press = ustruct.pack('f', client_data.PRESSURE) # create bytes format
        self.char_lp_temp.write(temp)
        self.char_lp_press.write(press)


    # def read_proto_value(self):
    #     proto = self.char_lp_proto.read().decode()
    #     print('Protocol choice read:', proto)
    #     return proto




# class ClientDataTest:
#     def __init__(self):
#         self.TEMPERATURE = 25
#         self.PRESSURE = 1000
#         self.HUMIDITY = 60
#         self.protocol = 'none'
#
# client_data = ClientDataTest()
# ble_clt = BleClientB()
#
# print('WESZLO DO BLE')
# TEST_FLAG = True
# ble_clt = BleClientB()
# while True:
#     conn = ble_clt.connect_to_server(client_data)
#     ble_clt.register_lps25hb_serv_and_char(conn)
#     client_data.protocol = ble_clt.read_proto_value()
#     if client_data.protocol != 'BLE': # stop thread
#         conn.disconnect()
#         del ble_clt
#         break
#     ble_clt.send_measurement_to_server(client_data)
#     conn.disconnect()
#     time.sleep(1)
