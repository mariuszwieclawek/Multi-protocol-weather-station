from network import Bluetooth
from machine import Timer
import pycom
import time

pycom.heartbeat(False)
pycom.rgbled(0x7f0000) # red
# pycom.rgbled(0x00FF00)  # Green
# pycom.rgbled(0x0000FF)  # Blue

def char_notify_callback(char):
    char_value = char.value()
    print('New value: {}'.format(char_value))
    conn.disconnect()


BLE_SERVER_NAME = 'WEATHER_STATION_BLE_SERVER'

bluetooth = Bluetooth()
bluetooth.start_scan(-1)    # start scanning - no timeout

while(True):
    advert = bluetooth.get_adv() # get advertisment from other bluetooth devices
    if(advert): # when we get some adv
        # print(advert)
        if bluetooth.resolve_adv_data(advert.data, Bluetooth.ADV_NAME_CMPL) == BLE_SERVER_NAME: #check if it is our weather station
            conn = bluetooth.connect(advert.mac)
            print('Connected to weather station')
            services = conn.services() # service search for connected BLE server
            # print(services)
            for service in services:
                # print(service)
                characteristics = service.characteristics()
                for chars in characteristics:
                    print(chars)
                    print(chars.properties())
                    char_uuid = chars.uuid()
                    if char_uuid == 0xec0e:
                        chars.callback(trigger=Bluetooth.CHAR_NOTIFY_EVENT, handler=char_notify_callback)
                        


                        
