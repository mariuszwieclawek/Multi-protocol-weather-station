from network import WLAN
import machine
import pycom
import time

pycom.heartbeat(False)
# pycom.rgbled(0x7f0000) # red
pycom.rgbled(0x00FF00)  # Green
# pycom.rgbled(0x0000FF)  # Blue

wlan = WLAN(mode=WLAN.STA)

# nets = wlan.scan()
while(True):
    nets = wlan.scan()
    print(nets)
    for net in nets:
        if net.ssid == 'mywifi':
            print('Network found!')
            wlan.connect(net.ssid, auth=(net.sec, 'mywifikey'), timeout=5000)
            while not wlan.isconnected():
                machine.idle() # save power while waiting
            print('WLAN connection succeeded!')
            break
    time.sleep(1)
