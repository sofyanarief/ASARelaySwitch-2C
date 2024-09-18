import ubinascii
import network
from time import sleep

class WifiManager:
    def __init__(self):
        self.apIf = network.WLAN(network.AP_IF)
        self.staIf = network.WLAN(network.STA_IF)
        macAddr = ubinascii.hexlify(self.apIf.config('mac')).decode().upper()
        macAddr = macAddr[-6:]
        self.deviceName = 'ASARS2' + macAddr
        self.operatingMode = ''
    
    def activateApMode(self):
        print('Settiing WiFi interface to Access Point mode')
        self.staIf.active(False)
        self.apIf.active(True)
        self.apIf.config(ssid=self.deviceName, security=network.AUTH_WPA_WPA2_PSK, key='12345678')
        sleep(20)
        print('The device is operating in Access Point mode. SSID of this device is ' + self.deviceName)
        print(self.apIf.ifconfig())
        self.operatingMode = 'ap'
    
    def activateStaMode(self, ssid, passwd):
        numRetry = 1
        while numRetry <=3:
            print('Trying to connect to WiFi with SSID: ' + str(ssid) + ' for the ' + str(numRetry) + ' time.')
            numRetry+=1
            self.apIf.active(False)
            self.staIf.active(True)
            self.staIf.connect(str(ssid), str(passwd))
            self.staIf.config(dhcp_hostname=self.deviceName)
            sleep(10)
            if self.staIf.isconnected() == True:
                print('The device is operating in Station mode and is connected to ' + str(ssid))
                print(self.staIf.ifconfig())
                self.operatingMode = 'sta'
                break