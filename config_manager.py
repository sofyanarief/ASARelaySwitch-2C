import json

class ConfigManager:
    def __init__(self):
        self.fileName = 'config.json'
        
    def readConfig(self):
        try:
            print('Reading '+ str(self.fileName) +' as config file.')
            with open(self.fileName, 'r') as file:
                config = json.load(file)
                return config
        except OSError:
            print('No configuration file found. Write an empty configuration file.')
            self.resetConfig()
            return {}
    
    def writeConfig(self, config):
        try:
            print('Writing config to '+ str(self.fileName))
            with open(self.fileName, 'w') as file:
                json.dump(config, file)
        except OSError as e:
            print("Failed to write configuration: " + str(e))
    
    def updateConfig(self, key, value):
        print('Updating '+ str(self.fileName) +', set value:'+ str(value) +' for '+key)
        config = self.readConfig()
        config[key] = value
        self.writeConfig(config)
        
    def resetConfig(self):
        config = {"ch1Pin": 0, "ch2Pin": 2, "deviceMode": "standalone"}
        for key, value in config.items():
            self.updateConfig(key,value)