import requests
import json 
import os
import logging
from requests.sessions import codes
from vpdconfig import VPDServer,VPDConfig
import shutil


logging.basicConfig(filename='/home/vpd/Desktop/log_upload.log',level=logging.INFO, format='%(asctime)s : %(levelname)s : %(message)s')

#################### LocalPath ###############
apppath = "/home/vpd/MoldDataLogviewJetson/VPDDatalog"#os.path.dirname(__file__)
#if(apppath == ''):
#    apppath = '.'
Mainlog = apppath +"/MachineLog/"
Uploadedlog = apppath +"/MachineLog/Uploaded/"
#################### SERVER ##################
serverconfig = VPDServer()
#################### Config ##################
config = VPDConfig()
config.load(serverconfig.Server)
#################### CreateDIR ###############
def createdir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

createdir(Mainlog)
createdir(Uploadedlog)

for k in range(3):
    #################### CheckFile ###############
    allfiles = [f for f in os.listdir(Mainlog) if os.path.isfile(os.path.join(Mainlog,f))]
    try:
        allfiles.remove('log.log')
    except:
        pass

    ################### Upload ##################
    if(len(allfiles) > 0):
        fileMainlocation = []
        fileMovelocation = []
        fileUploadServer = []
        for i in allfiles:
            fileMainlocation.append(Mainlog+i)
            fileMovelocation.append(Uploadedlog+i)
            fileUploadServer.append(('files',open(Mainlog+i,'rb')))

        url = serverconfig.CIM_API
        header = { 'Token': serverconfig.CIM_API_TOKEN }
        data = {
                'mc_id': config.MACHINE_NO,
                'model': config.MACHINE_MODEL,
                'operation': config.OPERATION,
                'host_name': serverconfig.CIM_HOST
                }
        autologViewData = { 
            'autologViewData': json.dumps(data)
            }
        try:
            r = requests.post(url,headers=header,files=fileUploadServer,data=autologViewData)
            code = r.status_code
            logging.info("Status Code : "+str(code))
            logging.info("Response Text : "+str(r.text))
            if(code == 200):
                logging.info("Uploaded.")
                try:
                    nfile = len(fileMainlocation)
                    for i in range(nfile):
                        shutil.move(fileMainlocation[i],fileMovelocation[i])
                    logging.info("Move "+str(nfile)+" file complete.")
                except:
                    logging.error("Move file error !!!")
                break
            else:
                logging.error("Status Code : "+str(code)+" Upload Error !!!")
        except:
            logging.info("Upload Error !!!")
            pass
    else:
        logging.error("Not found log file !!!")

