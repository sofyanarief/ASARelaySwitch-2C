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
                    if e.errno == 104:  # ECONNRESET
                        print('Connection reset by peer')
                    else:
                        print('OSError: ', e)
                finally:
                    conn.close()
            except Exception as e:
                print('Error accepting connection: ', e)

    def urlDecode(self, encodedUrl):
        # print('encode: '+encodedUrl)
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
        # print('resutl: '+result)
        return result
                    
    def handleRequest(self, strRequest):
        getData = []
        paramData = {}
        reqUrl = ''
        arrReqUrl = []
        requestLines = strRequest.split('\n')
        # print('requestLines: '+str(requestLines))
        
        if len(requestLines) > 0:
            method, reqUrl, _ = requestLines[0].split(' ')
            reqUrl = reqUrl[1:]
        else:
            method = 'GET'
            path = '/'
        
        # print('requestUrl: '+ str(reqUrl))

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

        # print('paramData: '+str(paramData))
        
        if path == '':
            return self.serveHomePage()
        elif path == 'setting':
            return self.serveSettingPage()
        elif path == 'savesetting':
            if len(paramData) > 0:
                return self.serveSaveSettingPage(paramData)
            else:
                return self.serveSettingPage()
        else:
            return self.serve404Page()
    
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
        htmlContent += '<div class="page-container">'
        htmlContent += '<h1 class="display-4">Welcome To ASA Technology</h1>'
        htmlContent += '<p class="lead">Glad you have ASA RelaySwitch 2 Channel version</p>'
        htmlContent += '&nbsp;<br>'
        htmlContent += '&nbsp;<br>'
        htmlContent += '&nbsp;<br>'
        htmlContent += '&nbsp;<br>'
        htmlContent += '&nbsp;<br>'
        htmlContent += '&nbsp;<br>'
        htmlContent += '<a href="setting">'
        htmlContent += '<button type="button" class="btn btn-primary btn-lg">Let\'s Start Your Journey</button>'
        htmlContent += '</a>'
        htmlContent += '</div>'
        htmlContent += self.readHtmlFooterFile()
        return htmlContent
    
    def serve404Page(self):
        htmlContent = ''
        htmlContent += self.readHtmlHeaderFile()
        htmlContent += '<h1 class="display-4">404</h1>'
        htmlContent += '<p class="lead">Sorry, page not found</p>'
        htmlContent += self.readHtmlFooterFile()
        return htmlContent
    
    def serveSettingPage(self):
        htmlContent = ''
        htmlContent += self.readHtmlHeaderFile()
        htmlContent += '<div class="page-container">'
        htmlContent += '<h1 class="display-4">ASA RelaySwitch 2 Channel Version</h1>'
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
        htmlContent += '</div>'
        htmlContent += self.readHtmlFooterFile()
        return htmlContent
    
    def serveSaveSettingPage(self,paramData):
        htmlContent = ''
        htmlContent += self.readHtmlHeaderFile()
        htmlContent += '<div class="page-container">'
        htmlContent += '<h1 class="display-4">ASA RelaySwitch 2 Channel Version</h1>'
        htmlContent += '<p class="lead">You have configure this device with this value:</p>'
        htmlContent += '<div class="content-box">'
        htmlContent += '<form action="savesetting" target="_self" method="get">'
        htmlContent += '<div class="form-group">'
        htmlContent += '<label for="ssid">WiFi Name:</label>'
        htmlContent += '<input class="form-control" type="text" name="ssid" value="'+paramData.get('ssid')+'" readonly>'
        htmlContent += '</div>'
        htmlContent += '<div class="form-group">'
        htmlContent += '<label for="passwd">WiFi Password:</label>'
        htmlContent += '<input class="form-control" type="text" name="passwd" value="'+paramData.get('passwd')+'" readonly>'
        htmlContent += '</div>'
        htmlContent += '<div class="form-group">'
        htmlContent += '<label for="mqttServer">MQTT Server:</label>'
        htmlContent += '<input class="form-control" type="text" name="mqttServer" value="'+paramData.get('mqttServer')+'" readonly>'
        htmlContent += '</div>'
        htmlContent += '<div class="form-group">'
        htmlContent += '<label for="ch1Topic">Channel 1 Topic:</label>'
        htmlContent += '<input class="form-control" type="text" name="ch1Topic" value="'+paramData.get('ch1Topic')+'" readonly>'
        htmlContent += '</div>'
        htmlContent += '<div class="form-group">'
        htmlContent += '<label for="ch2Topic">Channel 2 Topic:</label>'
        htmlContent += '<input class="form-control" type="text" name="ch2Topic" value="'+paramData.get('ch2Topic')+'" readonly>'
        htmlContent += '</div>'
        htmlContent += '</form>'
        htmlContent += '<p>Device will restart in 10 second for applying setting.</p>'
        htmlContent += '</div>'
        htmlContent += '</div>'
        htmlContent += self.readHtmlFooterFile()
        configManagerObj = ConfigManager()
        for key, value in paramData.items():
            configManagerObj.updateConfig(key,value)
        else:
            self.restartFlag = True
        return htmlContent