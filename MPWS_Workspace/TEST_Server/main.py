from network import Bluetooth
from machine import Timer
import pycom
import time

pycom.heartbeat(False)
pycom.rgbled(0x0000FF)  # Blue


def conn_cb(chr):
    events = chr.events()
    if events & Bluetooth.CLIENT_CONNECTED:
        print('client connected')
    elif events & Bluetooth.CLIENT_DISCONNECTED:
        print('client disconnected')


def chr_temp_am_handler(chr):
    events = chr.events()
    if events & (Bluetooth.CHAR_READ_EVENT):
        char_value = chr.value()
        print('Odczyt z am_temp: {}'.format(char_value))
    if events & Bluetooth.CHAR_WRITE_EVENT:
        print("Write request with value = {}".format(chr.value()))

def chr_hum_am_handler(chr):
    events = chr.events()
    if events & (Bluetooth.CHAR_READ_EVENT | Bluetooth.CHAR_SUBSCRIBE_EVENT):
        char_value = chr.value()
        print('Odczyt z am_hum: {}'.format(char_value))

def chr_temp_lp_handler(chr):
    events = chr.events()
    if events & (Bluetooth.CHAR_READ_EVENT | Bluetooth.CHAR_SUBSCRIBE_EVENT):
        char_value = chr.value()
        print('Odczyt z lp_temp: {}'.format(char_value))

def chr_press_lp_handler(chr):
    events = chr.events()
    if events & (Bluetooth.CHAR_READ_EVENT | Bluetooth.CHAR_SUBSCRIBE_EVENT):
        char_value = chr.value()
        print('Odczyt z lp_press: {}'.format(char_value))


bluetooth = Bluetooth()
bluetooth.set_advertisement(name='WEATHER_STATION_BLE_SERVER')
bluetooth.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=conn_cb)
bluetooth.advertise(True)

srv_am2320 = bluetooth.service(uuid=0x0001, isprimary=True, nbr_chars=2)
srv_lps25hb = bluetooth.service(uuid=0x0002, isprimary=True, nbr_chars=2)

chr_temp_am = srv_am2320.characteristic(uuid=0x0010)
chr_hum_am = srv_am2320.characteristic(uuid=0x0011)

chr_temp_lp = srv_lps25hb.characteristic(uuid=0x0020)
chr_press_lp = srv_lps25hb.characteristic(uuid=0x0021)

chr_temp_am.callback(trigger=(Bluetooth.CHAR_READ_EVENT), handler=chr_temp_am_handler)
chr_hum_am.callback(trigger=(Bluetooth.CHAR_READ_EVENT | Bluetooth.CHAR_SUBSCRIBE_EVENT), handler=chr_hum_am_handler)
chr_temp_lp.callback(trigger=(Bluetooth.CHAR_READ_EVENT | Bluetooth.CHAR_SUBSCRIBE_EVENT), handler=chr_temp_lp_handler)
chr_press_lp.callback(trigger=(Bluetooth.CHAR_READ_EVENT | Bluetooth.CHAR_SUBSCRIBE_EVENT), handler=chr_press_lp_handler)

print('Start BLE service')

i = 0
while True:
    print(i)
    chr_temp_am.value(i)
    chr_hum_am.value(i+10)
    chr_temp_lp.value(i+20)
    chr_press_lp.value(i+30)
    i += 1
    time.sleep(2)
