import paho.mqtt.client as mqtt #import the client1
import json
import time

a = 1 #round pub
broker_address="127.0.0.1"
#broker_address="pca571.nseb.co.th"
MQTT_TOPIC = "vpd_all/midnight"
MQTT_MSG=json.dumps({"time":"midnight"})

for i in range(a):
    time.sleep(5)
    client = mqtt.Client("vpdtest") #create new instance
    client.connect(broker_address) #connect to broker
    client.publish(MQTT_TOPIC,MQTT_MSG) #publish