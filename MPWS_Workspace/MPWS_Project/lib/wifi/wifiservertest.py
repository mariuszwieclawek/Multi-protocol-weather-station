from network import WLAN
import pycom
import time

pycom.heartbeat(False)
# pycom.rgbled(0x7f0000) # red
pycom.rgbled(0x00FF00)  # Green
# pycom.rgbled(0x0000FF)  # Blue

wlan = WLAN()

wlan.init(mode=WLAN.AP, ssid='hello world', antenna=WLAN.INT_ANT)
#use the line below to apply a password
#wlan.init(ssid="hi", auth=(WLAN.WPA2, "eightletters"))
print(wlan.ifconfig(id=1)) #id =1 signifies the AP interface