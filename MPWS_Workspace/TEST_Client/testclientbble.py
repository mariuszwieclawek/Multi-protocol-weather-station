from network import Bluetooth
from machine import Timer
import pycom
import time
import ustruct

pycom.heartbeat(False)
# pycom.rgbled(0x7f0000) # red
pycom.rgbled(0x00FF00)  # Green
# pycom.rgbled(0x0000FF)  # Blue



class BleClientB(Bluetooth):
    def __init__(self):
        self.BLE_SERVER_NAME = 'WEATHER_STATION_BLE_SERVER'
        self.lps25hb_meas_service_uuid = 0x0020
        self.lps25hb_prot_service_uuid = 0x0021
        self.lps25hb_meas_serv_temp_char_uuid = 0x0200
        self.lps25hb_meas_serv_press_char_uuid = 0x0201
        self.lps25hb_prot_serv_char_uuid = 0x0250
        self.srv_lps25hb = 0
        self.srv_lps25hb_proto = 0
        self.char_lp_temp = 0
        self.char_lp_press = 0
        self.char_lp_proto = 0
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


    def register_lps25hb_serv_and_char(self, conn):
        services = conn.services() # service search for connected BLE server
        for service in services:
            service_uuid = service.uuid()
            if service_uuid == self.lps25hb_meas_service_uuid:
                print('LPS25HB')
                self.srv_lps25hb = service
                characteristics = service.characteristics()
                for char in characteristics:
                    char_uuid = char.uuid()
                    if char_uuid == self.lps25hb_meas_serv_temp_char_uuid: # char for send temperature
                        print('LPS25HB_TEMP')
                        self.char_lp_temp = char
                    elif char_uuid == self.lps25hb_meas_serv_press_char_uuid: # char for send pressure
                        print('LPS25HB_PRESS')
                        self.char_lp_press = char
            elif service_uuid == self.lps25hb_prot_service_uuid:
                print('PROTO')
                self.srv_lps25hb_proto = service
                characteristics = service.characteristics()
                for char in characteristics:
                    char_uuid = char.uuid()
                    if char_uuid == self.lps25hb_prot_serv_char_uuid: # char for proto choice receive
                        print('PROTO_CHAR')
                        self.char_lp_proto = char
                        self.char_lp_proto.callback(trigger=Bluetooth.CHAR_NOTIFY_EVENT, handler=self.chr_proto_lp_notify_callback)


    # Callback when get new protocol choice
    def chr_proto_lp_notify_callback(self, char):
        char_value = char.value()
        print('New proto choice: ', char_value)
        self.proto_choice_get = True


    def send_measurement_to_server(self, lps25hb):
        temp = ustruct.pack('f', lps25hb.temp) # create bytes format
        press = ustruct.pack('f', lps25hb.press) # create bytes format
        print('Send temperature')
        self.char_lp_temp.write(temp)
        print('Send pressure')
        self.char_lp_press.write(press)


    def send_proto_get_confirmation(self):
        if self.proto_choice_get == True:
            print('Send proto get confirmation')
            self.char_lp_proto.write('TRUE')
            self.proto_choice_get = False

class lps25Test:
    def __init__(self):
        self.temp = 25.5
        self.press = 1000.5

lps25 = lps25Test()
ble_clt = BleClientB()

while True:
    conn = ble_clt.connect_to_server()
    ble_clt.register_lps25hb_serv_and_char(conn)
    ble_clt.send_measurement_to_server(lps25)
    ble_clt.send_proto_get_confirmation()
    conn.disconnect()
    time.sleep(5)
