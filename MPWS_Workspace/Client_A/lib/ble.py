from network import Bluetooth
from machine import Timer
import pycom
import time
import ustruct


class BleClientA(Bluetooth):
    def __init__(self):
        self.BLE_SERVER_NAME = 'WEATHER_STATION_BLE_SERVER'
        self.am2320_meas_service_uuid = 0x0010
        self.am2320_prot_service_uuid = 0x0011
        self.am2320_meas_serv_temp_char_uuid = 0x0100
        self.am2320_meas_serv_hum_char_uuid = 0x0101
        self.am2320_prot_serv_char_uuid = 0x0150
        self.srv_am2320 = 0
        self.srv_am2320_proto = 0
        self.char_am_temp = 0
        self.char_am_hum = 0
        self.char_am_proto = 0
        self.conn = 0
        self.proto_choice_get = False


    def connect_to_server(self):
        print('Start scanning for BLE Server')
        self.start_scan(-1)    # start scanning - no timeout
        while True:
            advert = self.get_adv() # get advertisment from other bluetooth devices
            if advert and self.resolve_adv_data(advert.data, Bluetooth.ADV_NAME_CMPL) == self.BLE_SERVER_NAME: #check if it is our weather station: # when we get some adv
                try:
                    self.conn = self.connect(advert.mac)
                except:
                    print('Cannot connect')
                    return False
                else:
                    print('Connected to weather station')
                    self.stop_scan()
                    return ble_clt.conn


    def register_am2320_serv_and_char(self, conn):
        services = conn.services() # service search for connected BLE server
        for service in services:
            service_uuid = service.uuid()
            if service_uuid == self.am2320_meas_service_uuid:
                print('am2320')
                self.srv_am2320 = service
                characteristics = service.characteristics()
                for char in characteristics:
                    char_uuid = char.uuid()
                    if char_uuid == self.am2320_meas_serv_temp_char_uuid: # char for send temperature
                        print('am2320_TEMP')
                        self.char_am_temp = char
                    elif char_uuid == self.am2320_meas_serv_hum_char_uuid: # char for send pressure
                        print('am2320_hum')
                        self.char_am_hum = char
            elif service_uuid == self.am2320_prot_service_uuid:
                print('PROTO')
                self.srv_am2320_proto = service
                characteristics = service.characteristics()
                for char in characteristics:
                    char_uuid = char.uuid()
                    if char_uuid == self.am2320_prot_serv_char_uuid: # char for proto choice receive
                        print('PROTO_CHAR')
                        self.char_am_proto = char
                        self.char_am_proto.callback(trigger=Bluetooth.CHAR_NOTIFY_EVENT, handler=self.chr_proto_lp_notify_callback)


    # Callback when get new protocol choice
    def chr_proto_lp_notify_callback(self, char):
        char_value = char.value()
        print('New proto choice: ', char_value)
        self.proto_choice_get = True


    def send_measurement_to_server(self, am2320):
        temp = ustruct.pack('f', am2320.temp) # create bytes format
        press = ustruct.pack('f', am2320.hum) # create bytes format
        print('Send temperature')
        self.char_am_temp.write(temp)
        print('Send humidity')
        self.char_am_hum.write(press)


    def send_proto_get_confirmation(self):
        if self.proto_choice_get == True:
            print('Send proto get confirmation')
            self.char_am_proto.write('TRUE')
            self.proto_choice_get = False


# am2320 = am2320Test()
# ble_clt = BleClientA()
#
# while True:
#     conn = ble_clt.connect_to_server()
#     ble_clt.register_am2320_serv_and_char(conn)
#     ble_clt.send_measurement_to_server(am2320)
#     ble_clt.send_proto_get_confirmation()
#     conn.disconnect()
#     time.sleep(5)
