from network import Bluetooth
from machine import Timer
import pycom
import time

pycom.heartbeat(False)
pycom.rgbled(0x7f0000) # red
# pycom.rgbled(0x00FF00)  # Green
# pycom.rgbled(0x0000FF)  # Blue

def chr_temp_am_notify_callback(char):
    char_value = char.value()
    print('New value am_temp: {}'.format(char_value))

def chr_hum_am_notify_callback(char):
    char_value = char.value()
    print('New value am_hum: {}'.format(char_value))


BLE_SERVER_NAME = 'WEATHER_STATION_BLE_SERVER'

bluetooth = Bluetooth()
bluetooth.start_scan(-1)    # start scanning - no timeout

while(True):
    advert = bluetooth.get_adv() # get advertisment from other bluetooth devices
    if(advert): # when we get some adv
        try:
            if bluetooth.resolve_adv_data(advert.data, Bluetooth.ADV_NAME_CMPL) == BLE_SERVER_NAME: #check if it is our weather station
                conn = bluetooth.connect(advert.mac)
                print('Connected to weather station')
                try:
                    services = conn.services() # service search for connected BLE server
                    for service in services:
                        characteristics = service.characteristics()
                        for chars in characteristics:
                            char_uuid = chars.uuid()
                            if char_uuid == 0x0010:
                                chars.callback(trigger=Bluetooth.CHAR_NOTIFY_EVENT, handler=chr_temp_am_notify_callback)
                            if char_uuid == 0x0011:
                                chars.callback(trigger=Bluetooth.CHAR_NOTIFY_EVENT, handler=chr_hum_am_notify_callback)
                except:
                    continue
        except:
            continue
