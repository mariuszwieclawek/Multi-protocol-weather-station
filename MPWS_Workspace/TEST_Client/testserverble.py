from network import Bluetooth
from machine import Timer
import pycom
import time
import ustruct

pycom.heartbeat(False)
pycom.rgbled(0x0000FF)  # Blue


class BleServer(Bluetooth):
    def __init__(self):
        self.BLE_SERVER_NAME = 'WEATHER_STATION_BLE_SERVER'
        # Services ID
        self.am2320_meas_service_uuid = 0x0010
        self.am2320_prot_service_uuid = 0x0011
        self.lps25hb_meas_service_uuid = 0x0020
        self.lps25hb_prot_service_uuid = 0x0021
        # Characteristics ID
        self.am2320_meas_serv_temp_char_uuid = 0x0100
        self.am2320_meas_serv_hum_char_uuid = 0x0101
        self.am2320_prot_serv_char_uuid = 0x0150
        self.lps25hb_meas_serv_temp_char_uuid = 0x0200
        self.lps25hb_meas_serv_press_char_uuid = 0x0201
        self.lps25hb_prot_serv_char_uuid = 0x0250
        # Services
        self.srv_am2320 = 0
        self.srv_am2320_proto = 0
        self.srv_lps25hb = 0
        self.srv_lps25hb_proto = 0
        # Characteristics
        self.char_am_temp = 0
        self.char_am_hum = 0
        self.char_am_proto = 0
        self.char_lp_temp = 0
        self.char_lp_press = 0
        self.char_lp_proto = 0
        # For protocol change in clients confirmation
        self.am2320_proto_conf = False
        self.lps25hb_proto_conf = False

        # Services AM2320 and LPS25HB sensors
        self.srv_am2320 = self.service(uuid=self.am2320_meas_service_uuid, isprimary=True, nbr_chars=2)
        self.srv_am2320_proto = self.service(uuid=self.am2320_prot_service_uuid, isprimary=True, nbr_chars=1)
        self.srv_lps25hb = self.service(uuid=self.lps25hb_meas_service_uuid, isprimary=True, nbr_chars=2)
        self.srv_lps25hb_proto = self.service(uuid=self.lps25hb_prot_service_uuid, isprimary=True, nbr_chars=1)

        # Characteristics AM2320 sensor
        self.chr_temp_am = self.srv_am2320.characteristic(uuid=self.am2320_meas_serv_temp_char_uuid)
        self.chr_hum_am = self.srv_am2320.characteristic(uuid=self.am2320_meas_serv_hum_char_uuid)
        self.chr_proto_am = self.srv_am2320_proto.characteristic(uuid=self.am2320_prot_serv_char_uuid)

        # Characteristics AM2320 sensor
        self.chr_temp_lp = self.srv_lps25hb.characteristic(uuid=self.lps25hb_meas_serv_temp_char_uuid)
        self.chr_press_lp = self.srv_lps25hb.characteristic(uuid=self.lps25hb_meas_serv_press_char_uuid)
        self.chr_proto_lp = self.srv_lps25hb_proto.characteristic(uuid=self.lps25hb_prot_serv_char_uuid, properties=Bluetooth.PROP_WRITE)

        # Callbacks AM2320 and LPS25HB sensors
        self.chr_temp_am.callback(trigger=(Bluetooth.CHAR_WRITE_EVENT), handler=self.chr_temp_am_handler)
        self.chr_hum_am.callback(trigger=(Bluetooth.CHAR_WRITE_EVENT), handler=self.chr_hum_am_handler)
        self.chr_temp_lp.callback(trigger=(Bluetooth.CHAR_WRITE_EVENT), handler=self.chr_temp_lp_handler)
        self.chr_press_lp.callback(trigger=(Bluetooth.CHAR_WRITE_EVENT), handler=self.chr_press_lp_handler)
        self.chr_proto_am.callback(trigger=(Bluetooth.CHAR_WRITE_EVENT), handler=self.chr_proto_am_handler)
        self.chr_proto_lp.callback(trigger=(Bluetooth.CHAR_WRITE_EVENT), handler=self.chr_proto_lp_handler)


    def start_ble_advertise(self):
        self.set_advertisement(name=self.BLE_SERVER_NAME)
        self.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=self.conn_cb)
        self.advertise(True)


    def send_new_proto_choice(self, proto):
        # Wait till confirmation that clients get the new protocol choice
        while True:
            self.chr_proto_lp.value(proto)
            self.chr_proto_am.value(proto)
            if self.am2320_proto_conf == True and self.lps25hb_proto_conf == True:
                self.am2320_proto_conf = False
                self.lps25hb_proto_conf = False
                break


    def conn_cb(self, bt):
        events = bt.events()
        if events & Bluetooth.CLIENT_CONNECTED:
            print('client connected')
        elif events & Bluetooth.CLIENT_DISCONNECTED:
            print('client disconnected')


    def chr_temp_am_handler(self, chr):
        events = chr.events()
        if events & Bluetooth.CHAR_WRITE_EVENT:
            data = ustruct.unpack('f', chr.value()) # measurement value
            print('Temperature from AM2320: ', data[0])


    def chr_hum_am_handler(self, chr):
        events = chr.events()
        if events & Bluetooth.CHAR_WRITE_EVENT:
            data = ustruct.unpack('f', chr.value()) # measurement value
            print('Humidity from AM2320: ', data[0])


    def chr_temp_lp_handler(self, chr):
        events = chr.events()
        if events & Bluetooth.CHAR_WRITE_EVENT:
            data = ustruct.unpack('f', chr.value()) # measurement value
            print('Temperature from LPS25HB: ', data[0])


    def chr_press_lp_handler(self, chr):
        events = chr.events()
        if events & Bluetooth.CHAR_WRITE_EVENT:
            data = ustruct.unpack('f', chr.value()) # measurement value
            print('Pressure from LPS25HB: ', data[0])


    def chr_proto_am_handler(self, chr):
        events = chr.events()
        if events & Bluetooth.CHAR_WRITE_EVENT:
            print('Proto confirmation from AM2320: ', str(chr.value()))
            if str(chr.value()) == 'TRUE':
                self.am2320_proto_conf = True


    def chr_proto_lp_handler(self, chr):
        events = chr.events()
        if events & Bluetooth.CHAR_WRITE_EVENT:
            print('Proto confirmation from LPS25HB: ', str(chr.value()))
            if str(chr.value()) == 'TRUE':
                self.lps25hb_proto_conf = True

ble_server = BleServer()
ble_server.start_ble_advertise()

print('Start BLE service')
while True:
    print('weszlo')
    # ble_server.send_new_proto_choice('WiFi')
    ble_server.chr_proto_lp.value('WiFi')
    ble_server.chr_proto_am.value('WiFi'``)
    print('wyszlo')
    time.sleep(2)
