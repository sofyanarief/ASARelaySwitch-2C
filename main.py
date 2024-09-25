from config_manager import ConfigManager
from wifi_manager import WifiManager
from web_server import WebServer
from mqtt_listener import MQTTListener
from time import sleep

configManagerObj = ConfigManager()
wifiManagerObj = WifiManager()

configDict = configManagerObj.readConfig()

def restartMachine():
    restartTimer = 10
    while restartTimer > 0:
        print('Restarting Device in '+str(restartTimer))
        sleep(1)
        restartTimer -=1
    print('System Is Restarted')
    machine.reset()
        
while True:
    if configDict.get('deviceName') != wifiManagerObj.deviceName:
        configManagerObj.updateConfig('deviceName', wifiManagerObj.deviceName)
        
    if configDict.get('deviceMode') == 'standalone':
        wifiManagerObj.activateApMode()
        webServerObj = WebServer()
    elif configDict.get('deviceMode') == 'infrastructure':
        if configDict.get('ssid') != None:
            wifiManagerObj.activateStaMode(configDict.get('ssid'), configDict.get('passwd'))
            if wifiManagerObj.staIf.isconnected() != True:
                configManagerObj.resetConfig()
                restartMachine()
            else:
                mqttListenerObj = MQTTListener()
                mqttListenerObj.subscribeTopic()
        else:
            configManagerObj.resetConfig()
            restartMachine()
    else:
        configManagerObj.resetConfig()
        restartMachine()
        
