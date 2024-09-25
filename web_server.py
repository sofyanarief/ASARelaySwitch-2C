from config_manager import ConfigManager
from time import sleep
import machine
import socket

class WebServer:
    def __init__(self):
        self.restartFlag = False
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', 80))
        sock.listen(5)
        while True:
            try:
                sendedParams = {}
                print('Web server is ready to get connection')
                conn, addr = sock.accept()
                print('Got a connection from %s' % str(addr))
                try:
                    request = conn.recv(1024)
                    strRequest = request.decode('utf-8')
                    print(str(strRequest))
                    response = self.handleRequest(strRequest)
                    conn.send('HTTP/1.1 200 OK\n')
                    conn.send('Content-Type: text/html\n')
                    conn.send('Connection: close\n\n')
                    conn.sendall(response)
                    if self.restartFlag is True:
                        restartTimer = 10
                        while restartTimer > 0:
                            print('Restarting Device in '+str(restartTimer))
                            sleep(1)
                            restartTimer -=1
                        print('System Is Restarted')
                        machine.reset()
                except OSError as e:
                    if e.errno == 104:
                        print('Connection reset by peer')
                    else:
                        print('OSError: ', e)
                finally:
                    conn.close()
            except Exception as e:
                print('Error accepting connection: ', e)

    def urlDecode(self, encodedUrl):
        result = ""
        i = 0
        while i < len(encodedUrl):
            if encodedUrl[i] == '%':
                hexValue = encodedUrl[i+1:i+3]
                result += chr(int(hexValue, 16))
                i += 3
            else:
                result += encodedUrl[i]
                i += 1
        return result
                    
    def handleRequest(self, strRequest):
        getData = []
        paramData = {}
        reqUrl = ''
        arrReqUrl = []
        requestLines = strRequest.split('\n')
        
        if len(requestLines) > 0:
            method, reqUrl, _ = requestLines[0].split(' ')
            reqUrl = reqUrl[1:]
        else:
            method = 'GET'
            path = '/'
        
        if '?' in reqUrl:
            arrReqUrl = reqUrl.split('?')
            path = arrReqUrl[0]
            getData = arrReqUrl[1]
            if '&' in getData:
                getData = getData.split('&')
                for elem in getData:
                    key, val = elem.split('=')
                    val = self.urlDecode(val)
                    paramData[key] = val
            else:
                key, val = getData.split('=')
                val = self.urlDecode(val)
                paramData[key] = val
        else:
            path = reqUrl
        
        if path == '':
            return self.serveHomePage()
        elif path == 'savesetting':
            if len(paramData) > 0:
                return self.serveSaveSettingPage(paramData)
            else:
                return self.serveHomePage()
        else:
            return self.serveHomePage()
    
    def readHtmlHeaderFile(self):
        htmlContent = ''
        try:
            with open('header.html', 'r') as htmlFile:
                 htmlContent = htmlFile.read()
        except OSError:
            print(' Header HTML file not found.')
        return htmlContent
                           
    def readHtmlFooterFile(self):
        htmlContent = ''
        try:
            with open('footer.html', 'r') as htmlFile:
                 htmlContent = htmlFile.read()
        except OSError:
            print(' Footer HTML file not found.')
        return htmlContent
                           
    def serveHomePage(self):
        htmlContent = ''
        htmlContent += self.readHtmlHeaderFile()
        htmlContent += '<p class="lead">Glad you have ASA RelaySwitch 2 Channel version</p>'
        htmlContent += '<p class="lead">Please fill form below to start using this device.</p>'
        htmlContent += '<div class="content-box">'
        htmlContent += '<form action="savesetting" target="_self" method="get">'
        htmlContent += '<div class="form-group">'
        htmlContent += '<label for="ssid">WiFi Name:</label>'
        htmlContent += '<input class="form-control" type="text" name="ssid">'
        htmlContent += '</div>'
        htmlContent += '<div class="form-group">'
        htmlContent += '<label for="passwd">WiFi Password:</label>'
        htmlContent += '<input class="form-control" type="text" name="passwd">'
        htmlContent += '</div>'
        htmlContent += '<div class="form-group">'
        htmlContent += '<label for="mqttServer">MQTT Server:</label>'
        htmlContent += '<input class="form-control" type="text" name="mqttServer">'
        htmlContent += '</div>'
        htmlContent += '<div class="form-group">'
        htmlContent += '<label for="ch1Topic">Channel 1 Topic:</label>'
        htmlContent += '<input class="form-control" type="text" name="ch1Topic">'
        htmlContent += '</div>'
        htmlContent += '<div class="form-group">'
        htmlContent += '<label for="ch2Topic">Channel 2 Topic:</label>'
        htmlContent += '<input class="form-control" type="text" name="ch2Topic">'
        htmlContent += '</div>'
        htmlContent += '<hr>'
        htmlContent += '<input class="form-control" type="hidden" name="deviceMode" value="infrastructure">'
        htmlContent += '<button type="submit" class="btn-success btn-lg">Save</button>'
        htmlContent += '</form>'
        htmlContent += '</div>'
        htmlContent += self.readHtmlFooterFile()
        return htmlContent
    
    def serveSaveSettingPage(self,paramData):
        htmlContent = ''
        htmlContent += self.readHtmlHeaderFile()
        htmlContent += '<p class="lead">You have configure this device with this value:</p>'
        htmlContent += '<div class="content-box">'
        htmlContent += '<p><b>WiFi Name:</b><br>'+paramData.get('ssid')+'</p>'
        htmlContent += '<p><b>WiFi Password:</b><br>'+paramData.get('passwd')+'</p>'
        htmlContent += '<p><b>MQTT Server:</b><br>'+paramData.get('mqttServer')+'</p>'
        htmlContent += '<p><b>Channel 1 Topic:</b><br>'+paramData.get('ch1Topic')+'</p>'
        htmlContent += '<p><b>Channel 2 Topic:</b><br>'+paramData.get('ch2Topic')+'</p>'
        htmlContent += '</div>'
        htmlContent += '<p>Device will restart in 10 second for applying setting.</p>'
        htmlContent += self.readHtmlFooterFile()
        configManagerObj = ConfigManager()
        for key, value in paramData.items():
            configManagerObj.updateConfig(key,value)
        else:
            self.restartFlag = True
        return htmlContent