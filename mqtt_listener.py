from time import sleep
from umqtt_simple import MQTTClient
from config_manager import ConfigManager
from relay_listener import RelayListener

class MQTTListener:
    def __init__(self):
       configManagerObj = ConfigManager()
       self.configDict = configManagerObj.readConfig()
       self.topicsToSubs = []
       self.relayListenerObj = RelayListener()
    
    def publishMessage(self, topic, message):
        client = MQTTClient(self.configDict.get('deviceName'), self.configDict.get('mqttServer'), 1883)
        try:
            print('Connecting to MQTT Server')
            client.connect()
        except:
            print('Can\'t connect to MQTT Server')
        else:
            print('Connected to MQTT Server')
            numRetry = 1
            while numRetry <=3:
                try:
                    print('Trying to publish message to MQTT Server for '+str(numRetry)+' time')
                    client.publish(topic, message)
                except:
                    print('Can\'t publish to MQTT Server')
                    numRetry += 1
                    sleep(1)
                else:
                    print('Message published on MQTT server')
                    break
            else:
                print('Can\'t publish to MQTT Server after 3 times retry')
            client.disconnect()

    def mqttCallback(self, topic, msg):
        topicStr = topic.decode('utf-8')
        msgStr = msg.decode('utf-8')
        print(f"Message received on topic: {topicStr}, message: {msgStr}")
        self.relayListenerObj.setRelayState(topicStr, msgStr)

    def connectAndSubscribe(self):
        for key, val in self.configDict.items():
            if "Topic" in key:
                self.topicsToSubs.append(val)
        client = MQTTClient(self.configDict.get('deviceName'), self.configDict.get('mqttServer'), 1883)
        client.set_callback(self.mqttCallback)

        try:
            print('Connecting to MQTT Server')
            client.connect()
        except:
            print('Can\'t connect to MQTT Server')
        else:
            print("Connected to MQTT Server")
            for val in self.topicsToSubs:
                numRetry = 1
                while numRetry <=3:
                    try:
                        print('Trying to subscribe '+val+' topic in MQTT Server for '+str(numRetry)+' time')
                        client.subscribe(val)
                    except:
                        print('Can\'t subscribe '+val+' topic in MQTT Server')
                        numRetry += 1
                        sleep(1)
                    else:
                        print("Subscribed to topic:", val)
                        break
                else:
                    print('Can\'t subscribe to MQTT Server after 3 times retry')
        return client

    def subscribeTopic(self):
        try:
            client = self.connectAndSubscribe()
            while True:
                client.check_msg()
                sleep(1)
        except OSError as e:
            print('Failed to connect:', e)

