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
        self.lock = _thread.allocate_lock()
        # Services ID
        self.am2320_meas_service_uuid = 0x0010
        # self.am2320_prot_service_uuid = 0x0011
        self.lps25hb_meas_service_uuid = 0x0020
        # self.lps25hb_prot_service_uuid = 0x0021
        # Characteristics ID
        self.am2320_meas_serv_temp_char_uuid = 0x0100
        self.am2320_meas_serv_hum_char_uuid = 0x0101
        # self.am2320_prot_serv_char_uuid = 0x0150
        self.lps25hb_meas_serv_temp_char_uuid = 0x0200
        self.lps25hb_meas_serv_press_char_uuid = 0x0201
        # self.lps25hb_prot_serv_char_uuid = 0x0250
        # Services
        self.srv_am2320 = 0
        # self.srv_am2320_proto = 0
        self.srv_lps25hb = 0
        # self.srv_lps25hb_proto = 0
        # Characteristics
        self.char_am_temp = 0
        self.char_am_hum = 0
        # self.char_am_proto = 0
        self.char_lp_temp = 0
        self.char_lp_press = 0
        # self.char_lp_proto = 0
        # # For protocol change in clients confirmation
        # self.am2320_proto_conf = False
        # self.lps25hb_proto_conf = False

        self.ble.set_advertisement(name=self.BLE_SERVER_NAME)
        self.ble.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=self.conn_cb)

        # Services AM2320 and LPS25HB sensors
        self.srv_am2320 = self.ble.service(uuid=self.am2320_meas_service_uuid, isprimary=True, nbr_chars=2)
        # self.srv_am2320_proto = self.ble.service(uuid=self.am2320_prot_service_uuid, isprimary=True, nbr_chars=1)
        self.srv_lps25hb = self.ble.service(uuid=self.lps25hb_meas_service_uuid, isprimary=True, nbr_chars=2)
        # self.srv_lps25hb_proto = self.ble.service(uuid=self.lps25hb_prot_service_uuid, isprimary=True, nbr_chars=1)

        # Characteristics AM2320 sensor
        self.chr_temp_am = self.srv_am2320.characteristic(uuid=self.am2320_meas_serv_temp_char_uuid)
        self.chr_hum_am = self.srv_am2320.characteristic(uuid=self.am2320_meas_serv_hum_char_uuid)
        # self.chr_proto_am = self.srv_am2320_proto.characteristic(uuid=self.am2320_prot_serv_char_uuid)

        # Characteristics AM2320 sensor
        self.chr_temp_lp = self.srv_lps25hb.characteristic(uuid=self.lps25hb_meas_serv_temp_char_uuid)
        self.chr_press_lp = self.srv_lps25hb.characteristic(uuid=self.lps25hb_meas_serv_press_char_uuid)
        # self.chr_proto_lp = self.srv_lps25hb_proto.characteristic(uuid=self.lps25hb_prot_serv_char_uuid)

        # Callbacks AM2320 and LPS25HB sensors
        # self.chr_temp_am.callback(trigger=(Bluetooth.CHAR_WRITE_EVENT), handler=self.chr_temp_am_handler)
        # self.chr_hum_am.callback(trigger=(Bluetooth.CHAR_WRITE_EVENT), handler=self.chr_hum_am_handler)
        # self.chr_temp_lp.callback(trigger=(Bluetooth.CHAR_WRITE_EVENT), handler=self.chr_temp_lp_handler)
        # self.chr_press_lp.callback(trigger=(Bluetooth.CHAR_WRITE_EVENT), handler=self.chr_press_lp_handler)
        # self.chr_proto_am.callback(trigger=(Bluetooth.CHAR_READ_EVENT), handler=self.chr_proto_am_handler)
        # self.chr_proto_lp.callback(trigger=(Bluetooth.CHAR_READ_EVENT), handler=self.chr_proto_lp_handler)


    def start_ble_advertise(self, server_data):
        self.server_data = server_data
        self.ble.advertise(True)


    def register_am2320_meas_callbacks(self):
        self.chr_temp_am.callback(trigger=(Bluetooth.CHAR_WRITE_EVENT), handler=self.chr_temp_am_handler)
        self.chr_hum_am.callback(trigger=(Bluetooth.CHAR_WRITE_EVENT), handler=self.chr_hum_am_handler)

    def register_lps25hb_meas_callbacks(self):
        self.chr_temp_lp.callback(trigger=(Bluetooth.CHAR_WRITE_EVENT), handler=self.chr_temp_lp_handler)
        self.chr_press_lp.callback(trigger=(Bluetooth.CHAR_WRITE_EVENT), handler=self.chr_press_lp_handler)


    # def set_protocol_choice_in_chars(self, server_data):
    #     self.chr_proto_am.value(server_data.protocol.encode())
    #     self.chr_proto_lp.value(server_data.protocol.encode())
    #     self.am2320_proto_conf = False
    #     self.lps25hb_proto_conf = False


    # def wait_for_clients_read_proto_choice(self):
    #     while self.am2320_proto_conf == False or self.lps25hb_proto_conf == False:
    #         pass # just wait


    # def check_exit_ble_connection(self, server_data):
    #     if server_data.protocol != 'BLE' and self.am2320_proto_conf == True and self.lps25hb_proto_conf == True:
    #         return True
    #     else:
    #         return False

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


    # def chr_proto_am_handler(self, chr):
    #     events = chr.events()
    #     if events & Bluetooth.CHAR_READ_EVENT:
    #         self.am2320_proto_conf = True
    #
    #
    # def chr_proto_lp_handler(self, chr):
    #     events = chr.events()
    #     if events & Bluetooth.CHAR_READ_EVENT:
    #         self.lps25hb_proto_conf = True



# def change_proto_thread(server_data):
#     while True:
#         time.sleep(25)
#         server_data.protocol = 'WiFi'
#         time.sleep(10)
#         server_data.protocol = 'BLE'
#
# server_data = ServerData()
# ble_server = BleServer()
# ble_server.start_ble_advertise()
# server_data.protocol = 'BLE'
# _thread.start_new_thread(change_proto_thread, (server_data, ))
# print('Start BLE service')
# while True:
#     # print('weszlo')
#     if server_data.protocol != server_data.protocol_buffer:
#         server_data.protocol_buffer = server_data.protocol
#         ble_server.set_protocol_choice_in_chars(server_data)
#         ble_server.wait_for_clients_read_proto_choice()
#         if ble_server.check_exit_ble_connection(server_data) ==  True: # stop ble work
#             print('New proto: ', server_data.protocol)
#             # ble_server.deinit()
#             del ble_server
#             break
#     # print('wyszlo')
