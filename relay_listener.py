from machine import Pin
from config_manager import ConfigManager

class RelayListener:
    def __init__(self):
        configManagerObj = ConfigManager()
        self.configDict = configManagerObj.readConfig()
        self.chTopicDict = {}
        self.chPinDict = {}
        self.chPinObjDict = {}
        for key, val in self.configDict.items():
            if key.endswith('Topic'):
                channel = key.replace('Topic', '')
                self.chTopicDict[channel] = val
            elif key.endswith('Pin'):
                channel = key.replace('Pin', '')
                self.chPinDict[channel] = val

        print(str(self.chTopicDict))
        print(str(self.chPinDict))

        for channel, pin_num in self.chPinDict.items():
            pinObj = Pin(pin_num, Pin.OUT)
            self.chPinObjDict[channel] = pinObj

    def setRelayState(self, topic, msg):
        for channel, topic_val in self.chTopicDict.items():
            if topic_val == topic:
                pinObj = self.chPinObjDict.get(channel)
                if msg == "ON":
                    pinObj.value(1)
                    print(f"Turning {channel} ON")
                elif msg == "OFF":
                    pinObj.value(0)
                    print(f"Turning {channel} OFF")