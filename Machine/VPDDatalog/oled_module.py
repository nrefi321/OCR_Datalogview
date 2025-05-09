import json
import time
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import subprocess
from threading import Thread, Lock,Semaphore
import paho.mqtt.client as mqtt
from vpdconfig import *
import os

#################### LocalPath ###############
apppath = os.path.dirname(__file__)
if(apppath == ''):
    apppath = '.'
resource = apppath +"/resource_OLED/"
print(resource)
#################### SERVER ##################
serverconfig = VPDServer()
#################### Config ##################
config = VPDConfig()
config.load(serverconfig.Server)
#################### MQTT #####################
mqtt_client = mqtt.Client()
MqttConnected = False
mutex = Lock() 
ReqReboot = False
statusupdate = 'Booting...'
################### OLED #####################
RST = None
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0
disp = Adafruit_SSD1306.SSD1306_128_64(rst=None, i2c_bus=1, gpio=1)
width = disp.width
height = disp.height
image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, width, height), outline=0, fill=0)
padding = -2
top = padding
bottom = height - padding
x = 0
y = 0

font = ImageFont.truetype(resource +'high_pixel-7.ttf', 9)
Hfont = ImageFont.truetype(resource +'Pixeland.ttf', 20)
stopfont = ImageFont.truetype(resource +'high_pixel-7.ttf', 14)
image1 = Image.open(resource +'cam.png').resize((disp.width, disp.height), Image.ANTIALIAS).convert('1')
#############################################

def onConnectedMqtt(self, client, userdata, rc):
    global config,mutex
    mutex.acquire()
    global MqttConnected
    MqttConnected = True
    mutex.release()
    subscribe = [(config.TOPIC_UPDATESTATUS,1),(config.TOPIC_REBOOT,1)]
    self.subscribe(subscribe)
    print("connected")

def onMessageMqtt(client, userdata,msg):
    global config,ReqReboot,statusupdate
    try:
        msgstr = msg.payload.decode("utf-8")
        #print(msg.topic)
        if(msg.topic == config.TOPIC_UPDATESTATUS):
            data = json.loads(msgstr)
            mutex.acquire()
            statusupdate = data['status']
            mutex.release()
        elif(msg.topic == config.TOPIC_REBOOT):
            mutex.acquire()
            ReqReboot = True
            mutex.release()
    except:
        pass

def connectMqtt():
    global serverconfig,mqtt_client
    port = 1883
    Server_ip = serverconfig.MQTTBroker
    mqtt_client.on_connect = onConnectedMqtt
    mqtt_client.on_message = onMessageMqtt
    mqtt_client.connect(Server_ip, port)
    mqtt_client.loop_start()
    #mqtt_client.loop_forever()

def disconnectMQTT():
    global mqtt_client
    try:
        mqtt_client.disconnect()
        mqtt_client.loop_stop()
    except:
        pass

def connectOLED():
    global disp,image1
    disp.begin()
    disp.clear()
    disp.display()
    disp.image(image1)
    disp.display()
    time.sleep(2)
    disp.clear()
    disp.display()

def loopProcess():
    global config,mutex,ReqReboot,statusupdate,image
    loc_stopprocess = False
    loc_reqReboot = False
    loc_status = statusupdate
    count_down = 10
    count = 0
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((x, top), "  Mold Datalog  ", font=Hfont, fill=255)
    draw.text((x, top + 21), "IP : " + config.DEVICE_IP, font=font, fill=255)
    draw.text((x, top + 32), "Machine No : "+config.MACHINE_NO, font=font, fill=255)
    draw.text((x, top + 43), "Device ID : "+config.DEVICE_ID, font=font, fill=255)
    disp.image(image)
    disp.display()
    while(loc_stopprocess == False):
        mutex.acquire()
        if(ReqReboot):
            loc_reqReboot = True
        loc_status = statusupdate
        mutex.release()
        if(loc_reqReboot == False):
            draw.rectangle((x-1, 64, width+1, 50), outline=0, fill=255)
            draw.text((x, top + 56), "Status : "+ loc_status, font=font, fill=0)
            disp.image(image)
            disp.display()
        else:
            print(count)
            if(count >= count_down):
                draw.rectangle((0, 0, width, height), outline=0, fill=0)
                disp.image(image)
                disp.display()
                os.popen("sudo -S %s"%('reboot'), 'w').write('vpd\n')
                return
            if(count == 0):
                disp.clear()
                disp.display()
                draw.rectangle((0, 0, width, height), outline=0, fill=0)
            draw.text((x, top + 15), "  I'll reboot in", font=stopfont, fill=255)
            draw.rectangle((x-1, 64, width+1, 40), outline=0, fill=255)
            draw.text((x, top + 50), "    "+str(count_down - count)+ " second.", font=stopfont, fill=0)
            #+str(count_down - count)+ " S"
            disp.image(image)
            disp.display()
            count+=1
            time.sleep(0.9)




def startupconnection():
    global MqttConnected
    mqttconnected = False
    oledconnected = False
    while(oledconnected == False):
        try:
            print('Connect OLED')
            connectOLED()
            oledconnected = True
        except:
            print('Connect Error')
            time.sleep(1)
    while(mqttconnected == False):
        connectMqtt()
        time.sleep(2)
        mutex.acquire()
        mqttconnected = MqttConnected
        print("MQTT Connected. ",MqttConnected)
        mutex.release()
        if(mqttconnected == True):
            print("MQTT Connect complete.")
            break
        else:
            print("Cannot Connect MQTT.")
            time.sleep(0.5)
        print("MQTT try to re connected.") 

    loopProcess()

startupconnection()




