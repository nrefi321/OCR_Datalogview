import requests
import json 
import os
import logging
from requests.sessions import codes
from vpdconfig import VPDServer,VPDConfig
import shutil

logging.basicConfig(filename=r'/home/vpd/Desktop/log_backupload.log',level=logging.INFO, format='%(asctime)s : %(levelname)s : %(message)s')

apppath = "/home/vpd/MoldDataLogviewJetson/VPDDatalog"#os.path.dirname(__file__)
Mainlog = apppath +"/MachineLog/"
serverlog = 'http://localhost:8888/log_file'

def createdir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

createdir(Mainlog)

for k in range(3):
    #################### CheckFile ###############
    allfiles = [f for f in os.listdir(Mainlog) if os.path.isfile(os.path.join(Mainlog,f))]
    try:
        allfiles.remove('log.log')
    except:
        pass

    if(len(allfiles) > 0):
        fileMainlocation = []
        # fileMovelocation = []
        fileUploadServer = []
        for i in allfiles:
            fileMainlocation.append(Mainlog+i)
            # fileMovelocation.append(Uploadedlog+i)
            fileUploadServer.append(('files',open(Mainlog+i,'rb')))

        print(fileUploadServer)
        try:
            # print('request')
            r = requests.post(serverlog, files = fileUploadServer)
            print(r)
            code = r.status_code
            logging.info("Backup Status Code : "+str(code))
            logging.info("Backup Response Text : "+str(r.text))
            if(code == 200):
                logging.info("Backup Uploaded.")
                break
            else:
                logging.error("Backup Status Code : "+str(code)+" Upload Error !!!")
        except:
            logging.info("Backup Upload Error !!!")
            pass

