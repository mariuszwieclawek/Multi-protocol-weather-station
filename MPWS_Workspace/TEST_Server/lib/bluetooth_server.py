from network import Bluetooth
from machine import Timer
import pycom
import time

pycom.heartbeat(False)
# pycom.rgbled(0x7f0000) # red
# pycom.rgbled(0x00FF00)  # Green
pycom.rgbled(0x0000FF)  # Blue


def conn_cb(chr):
    events = chr.events()
    if events & Bluetooth.CLIENT_CONNECTED:
        print('client connected')
    elif events & Bluetooth.CLIENT_DISCONNECTED:
        print('client disconnected')


def chr1_handler(chr, data):
    events = chr.events()
    print("events: ",events)
    if events & (Bluetooth.CHAR_READ_EVENT | Bluetooth.CHAR_SUBSCRIBE_EVENT):
        chr.value('test')


bluetooth = Bluetooth()
bluetooth.set_advertisement(name='WEATHER_STATION_BLE_SERVER', service_uuid=0xec00)
bluetooth.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=conn_cb)
bluetooth.advertise(True)

srv1 = bluetooth.service(uuid=0xec00, isprimary=True,nbr_chars=1)

chr1 = srv1.characteristic(uuid=0xec0e, value='read_from_here') #client reads from here
chr1.callback(trigger=(Bluetooth.CHAR_READ_EVENT | Bluetooth.CHAR_SUBSCRIBE_EVENT), handler=chr1_handler)
print('Start BLE service')

i = 0
while True:
    print(i)
    chr1.value(i)
    i += 1
    time.sleep(1)
