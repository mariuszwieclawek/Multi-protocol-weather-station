from network import Bluetooth
from machine import Timer
import pycom
import time
import ustruct
import _thread

pycom.heartbeat(False)
pycom.rgbled(0x0000FF)  # Blue


class BleServer():
    def __init__(self):
        self.ble = Bluetooth()
        self.BLE_SERVER_NAME = 'WEATHER_STATION_BLE_SERVER'
        # Services ID
        self.am2320_meas_service_uuid = 0x0010
        self.lps25hb_meas_service_uuid = 0x0020
        # Characteristics ID
        self.am2320_meas_serv_temp_char_uuid = 0x0100
        self.am2320_meas_serv_hum_char_uuid = 0x0101
        self.lps25hb_meas_serv_temp_char_uuid = 0x0200
        self.lps25hb_meas_serv_press_char_uuid = 0x0201
        # Services
        self.srv_am2320 = 0
        self.srv_lps25hb = 0
        # Characteristics
        self.char_am_temp = 0
        self.char_am_hum = 0
        self.char_lp_temp = 0
        self.char_lp_press = 0

        self.ble.set_advertisement(name=self.BLE_SERVER_NAME)
        self.ble.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=self.conn_cb)

        # Services AM2320 and LPS25HB sensors
        self.srv_am2320 = self.ble.service(uuid=self.am2320_meas_service_uuid, isprimary=True, nbr_chars=2)
        self.srv_lps25hb = self.ble.service(uuid=self.lps25hb_meas_service_uuid, isprimary=True, nbr_chars=2)

        # Characteristics AM2320 sensor
        self.chr_temp_am = self.srv_am2320.characteristic(uuid=self.am2320_meas_serv_temp_char_uuid)
        self.chr_hum_am = self.srv_am2320.characteristic(uuid=self.am2320_meas_serv_hum_char_uuid)

        # Characteristics AM2320 sensor
        self.chr_temp_lp = self.srv_lps25hb.characteristic(uuid=self.lps25hb_meas_serv_temp_char_uuid)
        self.chr_press_lp = self.srv_lps25hb.characteristic(uuid=self.lps25hb_meas_serv_press_char_uuid)


    def start_ble_advertise(self, server_data):
        self.server_data = server_data
        self.ble.advertise(True)


    def register_am2320_meas_callbacks(self):
        self.chr_temp_am.callback(trigger=(Bluetooth.CHAR_WRITE_EVENT), handler=self.chr_temp_am_handler)
        self.chr_hum_am.callback(trigger=(Bluetooth.CHAR_WRITE_EVENT), handler=self.chr_hum_am_handler)

    def register_lps25hb_meas_callbacks(self):
        self.chr_temp_lp.callback(trigger=(Bluetooth.CHAR_WRITE_EVENT), handler=self.chr_temp_lp_handler)
        self.chr_press_lp.callback(trigger=(Bluetooth.CHAR_WRITE_EVENT), handler=self.chr_press_lp_handler)


    def conn_cb(self, bt):
        events = bt.events()
        if events & Bluetooth.CLIENT_CONNECTED:
            pass
            # print('client connected')
        elif events & Bluetooth.CLIENT_DISCONNECTED:
            pass
            # print('client disconnected')


    def chr_temp_am_handler(self, chr):
        events = chr.events()
        if events & Bluetooth.CHAR_WRITE_EVENT:
            data = ustruct.unpack('f', chr.value()) # measurement value
            self.server_data.AM2320_TEMPERATURE = data[0]
            print('BLE -> Temperature - AM2320  = ', data[0])


    def chr_hum_am_handler(self, chr):
        events = chr.events()
        if events & Bluetooth.CHAR_WRITE_EVENT:
            data = ustruct.unpack('f', chr.value()) # measurement value
            self.server_data.AM2320_HUMIDITY = data[0]
            print('BLE -> Humidity    - AM2320  = ', data[0])


    def chr_temp_lp_handler(self, chr):
        events = chr.events()
        if events & Bluetooth.CHAR_WRITE_EVENT:
            data = ustruct.unpack('f', chr.value()) # measurement value
            self.server_data.LPS25HB_TEMPERATURE = data[0]
            print('BLE -> Temperature - LPS25HB = ', data[0])


    def chr_press_lp_handler(self, chr):
        events = chr.events()
        if events & Bluetooth.CHAR_WRITE_EVENT:
            data = ustruct.unpack('f', chr.value()) # measurement value
            self.server_data.LPS25HB_PRESSURE = data[0]
            print('BLE -> Pressure    - LPS25HB = ', data[0])
