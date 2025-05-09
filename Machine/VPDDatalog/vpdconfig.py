from re import search
import os
import json
import netifaces as ni
import requests
import paho.mqtt.publish as publish
from threading import Thread,Lock
import subprocess
import logging
import logging.handlers as handlers
import time

mutex = Lock()
logger = []
loggeractivated = False

configMainPath = "/home/vpd/MoldDataLogviewJetson/VPDDatalog"

class VPDConfig():
    
    config_dir = ''
    def __init__(self):
        global configMainPath
        self.DEVICE_ID = 'vpd01'
        self.DEVICE_IP = '127.0.0.1'
        self.MACHINE_NO = 'AGP-056'
        self.MACHINE_MODEL = 'GP-ELFD12042'
        self.OPERATION = 'MOLD'
        self.TOPIC_UPDATERECIPE = self.DEVICE_ID+'/loadRecipe'
        self.TOPIC_UPDATESTATUS = self.DEVICE_ID+'/status'
        self.TOPIC_UPDATEDATA = self.DEVICE_ID+'/updatedata'
        self.TOPIC_PUB_TAKEPICTURE = self.DEVICE_ID+'req_takepicture'
        self.TOPIC_SUB_TAKEPICTURE = self.DEVICE_ID+'/ret_takepicture'
        self.TOPIC_REBOOT = self.DEVICE_ID+'/reboot'
        self.TOPIC_MidnightAlarmClock = 'vpd_all/midnight'
        apppath = configMainPath #os.path.dirname(__file__)
        #if(apppath == ''):
        #    apppath = '.'
        VPDConfig.config_dir = apppath +"/VPDConfig/config/"

    def getIP(self,device= 'wlan0'):
        try:
            #cmd = "hostname -I | cut -d\' \' -f1"
            #ip = str(subprocess.check_output(cmd, shell=True),'utf-8')
            ip = ni.ifaddresses(device)[ni.AF_INET][0]['addr']
            #print('local ip = ',ip)
            return ip
        except:
            return '127.0.0.1'
    
    def createdir(self):
        config_dir = VPDConfig.config_dir
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            
    def loadDeviceIDAndIP(self,ip):
        self.createdir()
        param = { 'DEVICE_ID' : 'vpd01', 'DEVICE_IP': ip}
        if not os.path.exists(VPDConfig.config_dir +'deviceIDandIP.json'):
            json_data = json.dumps(param , indent=2)
            f = open(VPDConfig.config_dir  + 'deviceIDandIP.json', 'w')
            f.write(json_data)
            f.close()
        with open(VPDConfig.config_dir +'deviceIDandIP.json') as file:
            param = json.load(file)
            param['DEVICE_IP'] = ip
        
        #print(param)
        #reinitial
        self.DEVICE_ID = param['DEVICE_ID'] 
        self.DEVICE_IP =  param['DEVICE_IP'] 
        self.TOPIC_UPDATERECIPE = self.DEVICE_ID+'/loadRecipe'
        self.TOPIC_UPDATESTATUS = self.DEVICE_ID+'/status'
        self.TOPIC_UPDATEDATA = self.DEVICE_ID+'/updatedata'
        self.TOPIC_PUB_TAKEPICTURE = self.DEVICE_ID+'/req_takepicture'
        self.TOPIC_SUB_TAKEPICTURE = self.DEVICE_ID+'/ret_takepicture'
        self.TOPIC_REBOOT = self.DEVICE_ID+'/reboot'
        return param

    def loadConfigFromServer(self,serverIP,deviceID,IP):
        try:
            
            path = 'http://'+serverIP+':8080/Config/'+deviceID+','+IP
            res =  requests.get(path,timeout=10)
            if res.status_code == 200:
                #print(res.content)
                res_js = json.loads(res.content)
                objdata = res_js[0]
                self.DEVICE_ID = objdata['DeviceID'] 
                self.DEVICE_IP =  objdata['DeviceIP']  
                self.MACHINE_NO = objdata['MachineNo'] 
                self.MACHINE_MODEL = objdata['MachineModel'] 
                self.OPERATION = objdata['Operation'] 
                self.TOPIC_UPDATERECIPE = objdata['Topic_UpdateRecipe'] 
                self.TOPIC_UPDATESTATUS = objdata['Topic_UpdateStatus'] 
                self.TOPIC_UPDATEDATA = objdata['Topic_UpdateData'] 
                self.TOPIC_PUB_TAKEPICTURE = objdata['Topic_Pub_TakePicture'] 
                self.TOPIC_SUB_TAKEPICTURE = objdata['Topic_Sub_TakePicture']
                self.TOPIC_REBOOT = objdata['Topic_Reboot']
        except:
            pass

    def load(self,serverIP):
        ip = self.getIP('eth0')
        self.loadDeviceIDAndIP(ip)
        self.loadConfigFromServer(serverIP,self.DEVICE_ID,self.DEVICE_IP)

class VPDLastMachineRecipe():
    config_dir = ''
    def __init__(self):
        global configMainPath
        self.LastRecipe = 'OCR'
        apppath = configMainPath#os.path.dirname(__file__)
        #if(apppath == ''):
        #    apppath = '.'
        VPDLastMachineRecipe.config_dir = apppath +"/VPDConfig/config/"
    
    def createdir(self):
        config_dir = VPDLastMachineRecipe.config_dir
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
    
    def loadlastRecipe(self):
        config_dir = VPDLastMachineRecipe.config_dir
        self.createdir()
        param = { 'Recipe' :  'OCR' }
        if not os.path.exists(config_dir +'lastRecipe.json'):
            lastrecipe ={ 'Recipe' :  'OCR' }
            json_data = json.dumps(lastrecipe , indent=2)
            f = open(config_dir + 'lastRecipe.json', 'x')
            f.write(json_data)
            f.close()
        with open(config_dir +'lastRecipe.json') as file:
            param = json.load(file)
            self.LastRecipe = param['Recipe']
        return param['Recipe']

    def savelastRecipe(self,recipeName = ""):
        config_dir = VPDLastMachineRecipe.config_dir
        if(recipeName == ""):
            return
        self.createdir()
        param = { 'Recipe' :  recipeName }
        json_data = json.dumps(param , indent=2)
        f = open(config_dir + 'lastRecipe.json', 'w')
        f.write(json_data)
        f.close()
        self.LastRecipe = recipeName
    
    def savelastRecipeServer(self,serverIP,deviceID,recipeName = ""):
        if(recipeName == ""):
            return
        try:
            path = 'http://'+serverIP+':8080/Recipe/LastRecipe'
            body = { "DEVICE_ID": deviceID,"LASTRECIPE": recipeName }
            response = requests.post(path,json=body)
        except:
            pass
    
    def loadlastRecipeServer(self,serverIP,deviceID):
        strlastrecipe = self.LastRecipe
        try:
            path = 'http://'+serverIP+':8080/Recipe/LastRecipe/'+deviceID
            res =  requests.get(path)
            if res.status_code == 200:
                res_js = json.loads(res.content)
                strlastrecipe = res_js[deviceID]
                self.savelastRecipe(strlastrecipe)
                self.LastRecipe = strlastrecipe
        except:
            self.LastRecipe = strlastrecipe

    def load(self,serverIP,deviceID):
        self.loadlastRecipe()
        self.loadlastRecipeServer(serverIP,deviceID)
        return self.LastRecipe
    
    def save(self,serverIP,deviceID,recipeName = ""):
        self.savelastRecipeServer(serverIP,deviceID,recipeName)
        self.savelastRecipe(recipeName)
        return

class VPDServer():
    config_dir = ''
    def __init__(self):
        global configMainPath
        self.MQTTBroker = '172.16.42.104'
        self.Server = '172.16.42.104'
        self.CIM_API = 'http://th1srcim1:83/WebApi_CIM/api/v1/AutologViewController/Uploadfile'
        self.CIM_API_TOKEN = 'F34677FE-0FBA-447D-AECD-18D43BA17880'
        self.CIM_HOST = "API_FIRE"
        apppath = configMainPath#os.path.dirname(__file__)
        #if(apppath == ''):
        #    apppath = '.'
        VPDServer.config_dir = apppath +"/VPDConfig/config/"
        self.loadconfig()
    
    def createdir(self):
        config_dir = VPDServer.config_dir
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

    def loadconfig(self):
        config_dir = VPDServer.config_dir
        self.createdir()
        param = {
                    "Server": "172.16.42.104",
                    "MQTTBroker": "172.16.42.104",
                    "CIM_API":"http://th1srcim1:83/WebApi_CIM/api/v1/AutologViewController/UploadFile",
                    "CIM_API_TOKEN":"F34677FE-0FBA-447D-AECD-18D43BA17880",
                    "CIM_HOST":"API_FIRE"
                }
        if not os.path.exists(config_dir +'server.json'):
            json_data = json.dumps(param , indent=2)
            f = open(config_dir + 'server.json', 'w')
            f.write(json_data)
            f.close()
        with open(config_dir +'server.json') as file:
            param = json.load(file)
            #print(param)
            self.MQTTBroker = param['MQTTBroker']
            self.Server = param['Server']
            self.CIM_API=param['CIM_API']
            self.CIM_API_TOKEN=param['CIM_API_TOKEN']
            self.CIM_HOST = param['CIM_HOST']

        return param
    
    #Not Use on this time
    def saveconfig(self,MQTTBroker= "",Server = ""):
        config_dir = VPDServer.config_dir
        if(MQTTBroker == "" or Server == ""):
            return
        self.createdir()
        param = {
                    "Server": "172.16.42.104",
                    "MQTTBroker": "172.16.42.104",
                    "CIM_API":"http://th1srcim1:83/WebApi_CIM/api/v1/AutologViewController/UploadFile",
                    "CIM_API_TOKEN":"F34677FE-0FBA-447D-AECD-18D43BA17880",
                    "CIM_HOST":"API_FIRE"
                }
        json_data = json.dumps(param , indent=2)
        f = open(config_dir + 'server.json', 'w')
        f.write(json_data)
        f.close()
        self.MQTTBroker = MQTTBroker
        self.Server = Server

class Logfile():
    log_dir = ''
    def __init__(self):
        global loggeractivated, configMainPath
        apppath = configMainPath#os.path.dirname(__file__)
        #if(apppath == ''):
        #    apppath = '.'
        Logfile.log_dir = apppath + "/MachineLog/"
        self.createdir()
        if(loggeractivated == False):
            self.activateLoger()
    def activateLoger(self):
        global loggeractivated,logger
        apppath = configMainPath#os.path.dirname(__file__)
        #if(apppath == ''):
        #    apppath = '.'
        log_dir = apppath + "/MachineLog/"
        logger = logging.getLogger('my_app')
        logger.setLevel(logging.INFO)
        logHandler = handlers.TimedRotatingFileHandler(log_dir+'log.log', when='midnight',interval=1)
        logHandler.setLevel(logging.INFO)
        logHandler.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
        logger.addHandler(logHandler)
        loggeractivated = True

    def createdir(self):
        log_dir = Logfile.log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    def writelog(self,log):
        global logger,mutex
        self.createdir()
        #logging.basicConfig(filename=Logfile.log_dir+'log.log',level=logging.INFO, format='%(asctime)s: %(message)s')
        #logging.info(log)
        mutex.acquire()
        logger.info(log)
        mutex.release()

class RecordAlarm(Thread):
    def __init__(self,serverIP,MQBrokIP,MQTopic,body):
        Thread.__init__(self)
        self.serverIP = serverIP
        self.MQBrokIP = MQBrokIP
        self.MQTopic = MQTopic
        self.body = body

    def run(self):
        path = 'http://'+self.serverIP+':8080/AlarmData/'
        # try:
        #     response = requests.post(path,json=self.body)
        # except:
        #     pass
        try:
            publish.single(self.MQTopic,json.dumps(self.body,indent=4),hostname = self.MQBrokIP)
        except:
            pass


    


#data = VPDLastMachineRecipe()
#data.save('172.16.42.104','vpd01','OCR')

#data = VPDConfig()
#data.load('172.16.42.104')
#print(data.TOPIC_REBOOT)

#data = VPDServer()
#print(data.Delay)
