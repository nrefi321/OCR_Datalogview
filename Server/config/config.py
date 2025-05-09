from datetime import datetime, date
from fastapi import APIRouter, Depends , Response , status
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import and_,desc,asc
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks
from .dbconfig import session,VPDconfig
from .configModel import VPDconff,VPDconf,VPDConfigModel
from pydantic.datetime_parse import datetime

config = APIRouter(
    prefix="/Config",
    tags=["Config"],
    responses={200: {"msg": "OK"}}
)

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()   

@config.get("/{deviceID},{IP}",status_code=200)
async def GetDeviceConfig(deviceID:str,IP:str,response: Response,db:Session=Depends(get_db)):
    try:
        dataedit = db.query(VPDconfig).filter(and_(VPDconfig.ACTIVEFLAG == True,VPDconfig.DEVICE_ID == deviceID)).first()
        if(dataedit is not None):
            if(IP != ""):
                dataedit.DEVICE_IP = IP
                dataedit.UPDATEDATE = datetime.now()
                db.add(dataedit)
                db.commit()
                db.refresh(dataedit)
                print(deviceID+' Update IP ' + IP)
    except:
        print('Update IP Error !!!')
        pass
    
    data = db.query(VPDconfig).filter(and_(VPDconfig.ACTIVEFLAG == True,VPDconfig.DEVICE_ID == deviceID)).first()
    if(data is None):
        response.status_code = 404
        return {'msg':'No Data'}
    res = []
    vpdconmodel = {}
    vpdconmodel['DeviceID'] = data.DEVICE_ID
    vpdconmodel['DeviceIP'] = data.DEVICE_IP
    vpdconmodel['MachineNo'] = data.MACHINE_NO
    vpdconmodel['MachineModel'] = data.MACHINE_MODEL
    vpdconmodel['Operation'] = data.OPERATION
    vpdconmodel['Topic_UpdateRecipe'] = data.TOPIC_UPDATERECIPE
    vpdconmodel['Topic_UpdateStatus'] = data.TOPIC_UPDATESTATUS
    vpdconmodel['Topic_UpdateData'] = data.TOPIC_UPDATEDATA
    vpdconmodel['Topic_Pub_TakePicture'] = data.TOPIC_PUB_TAKEPICTURE
    vpdconmodel['Topic_Sub_TakePicture'] = data.TOPIC_SUB_TAKEPICTURE
    vpdconmodel['Topic_Reboot'] = data.TOPIC_REBOOT
    res.append(vpdconmodel)
    response.status_code = status.HTTP_200_OK
    return res

@config.get("/{deviceID}",status_code=200)
async def GetDeviceConfig(deviceID:str,response: Response,db:Session=Depends(get_db)):
    data = db.query(VPDconfig).filter(and_(VPDconfig.ACTIVEFLAG == True,VPDconfig.DEVICE_ID == deviceID)).first()
    if(data is None):
        response.status_code = 404
        return {'msg':'No Data'}
    res = []
    vpdconmodel = {}
    vpdconmodel['DeviceID'] = data.DEVICE_ID
    vpdconmodel['DeviceIP'] = data.DEVICE_IP
    vpdconmodel['MachineNo'] = data.MACHINE_NO
    vpdconmodel['MachineModel'] = data.MACHINE_MODEL
    vpdconmodel['Operation'] = data.OPERATION
    vpdconmodel['Topic_UpdateRecipe'] = data.TOPIC_UPDATERECIPE
    vpdconmodel['Topic_UpdateStatus'] = data.TOPIC_UPDATESTATUS
    vpdconmodel['Topic_UpdateData'] = data.TOPIC_UPDATEDATA
    vpdconmodel['Topic_Pub_TakePicture'] = data.TOPIC_PUB_TAKEPICTURE
    vpdconmodel['Topic_Sub_TakePicture'] = data.TOPIC_SUB_TAKEPICTURE
    vpdconmodel['Topic_Reboot'] = data.TOPIC_REBOOT
    res.append(vpdconmodel)
    response.status_code = status.HTTP_200_OK
    return res
    
@config.get("/",status_code=200)
async def GetDeviceConfig(response: Response,db:Session=Depends(get_db)):
    data = db.query(VPDconfig).filter(VPDconfig.ACTIVEFLAG == True).order_by(asc(VPDconfig.DEVICE_ID)).all()
    if(data is None):
        response.status_code = 404
        return {'msg':'No Data'}
    res = []
    for i in data:
        vpdconmodel = {}
        vpdconmodel['DeviceID'] = i.DEVICE_ID
        vpdconmodel['DeviceIP'] = i.DEVICE_IP
        vpdconmodel['MachineNo'] = i.MACHINE_NO
        vpdconmodel['MachineModel'] = i.MACHINE_MODEL
        vpdconmodel['Operation'] = i.OPERATION
        vpdconmodel['Topic_UpdateRecipe'] = i.TOPIC_UPDATERECIPE
        vpdconmodel['Topic_UpdateStatus'] = i.TOPIC_UPDATESTATUS
        vpdconmodel['Topic_UpdateData'] = i.TOPIC_UPDATEDATA
        vpdconmodel['Topic_Pub_TakePicture'] = i.TOPIC_PUB_TAKEPICTURE
        vpdconmodel['Topic_Sub_TakePicture'] = i.TOPIC_SUB_TAKEPICTURE
        vpdconmodel['Topic_Reboot'] = i.TOPIC_REBOOT
        res.append(vpdconmodel)
    response.status_code = status.HTTP_200_OK
    return res

@config.post("/",status_code=201)
async def PostDeviceConfig(response: Response,vpdrequest: VPDconf, backgroundtask: BackgroundTasks, db:session = Depends(get_db)):
    datacheck = db.query(VPDconfig).filter(VPDconfig.DEVICE_ID == vpdrequest.DeviceID).first()
    if(datacheck is not None):
        datacheck.DEVICE_ID=vpdrequest.DeviceID
        datacheck.DEVICE_IP=vpdrequest.DeviceIP
        datacheck.MACHINE_NO=vpdrequest.MachineNo
        datacheck.MACHINE_MODEL=vpdrequest.MachineModel
        datacheck.OPERATION=vpdrequest.Operation
        datacheck.TOPIC_UPDATERECIPE = vpdrequest.DeviceID+"/loadRecipe"
        datacheck.TOPIC_UPDATESTATUS = vpdrequest.DeviceID+"/status"
        datacheck.TOPIC_UPDATEDATA = vpdrequest.DeviceID+"/updatedata"
        datacheck.TOPIC_PUB_TAKEPICTURE = vpdrequest.DeviceID+"/req_takepicture"
        datacheck.TOPIC_SUB_TAKEPICTURE = vpdrequest.DeviceID+"/ret_takepicture"
        datacheck.TOPIC_REBOOT = vpdrequest.DeviceID+"/reboot"
        datacheck.UPDATEDATE = datetime.now()
        db.commit()
        db.refresh(datacheck)
        response.status_code = status.HTTP_201_CREATED
        return { 'msg' : 'Updated' }
    else:
        VPD = VPDconfig()
        VPD.DEVICE_ID = vpdrequest.DeviceID
        VPD.DEVICE_IP = vpdrequest.DeviceIP
        VPD.MACHINE_NO = vpdrequest.MachineNo
        VPD.MACHINE_MODEL = vpdrequest.MachineModel
        VPD.OPERATION = vpdrequest.Operation
        VPD.TOPIC_UPDATERECIPE = vpdrequest.DeviceID+"/loadRecipe";
        VPD.TOPIC_UPDATESTATUS = vpdrequest.DeviceID+"/status";
        VPD.TOPIC_UPDATEDATA = vpdrequest.DeviceID+"/updatedata";
        VPD.TOPIC_PUB_TAKEPICTURE = vpdrequest.DeviceID+"/req_takepicture";
        VPD.TOPIC_SUB_TAKEPICTURE = vpdrequest.DeviceID+"/ret_takepicture";
        VPD.TOPIC_REBOOT = vpdrequest.DeviceID+"/reboot";
        VPD.UPDATEDATE = datetime.now()
        db.add(VPD)
        db.commit()
        response.status_code = status.HTTP_201_CREATED
        return { 'msg':'Created'}

@config.put('/{deviceID}',status_code=201)
async def PutDeviceConfig(deviceID:str,conf:VPDconf,response: Response,db:Session=Depends(get_db)):
    vpd = db.query(VPDconfig).filter(VPDconfig.DEVICE_ID == deviceID).first()
    if(vpd is None):
        response.status_code = 404
        return {'msg':'No Data'}
    vpd.DEVICE_ID=conf.DeviceID
    vpd.DEVICE_IP=conf.DeviceIP
    vpd.MACHINE_NO=conf.MachineNo
    vpd.MACHINE_MODEL=conf.MachineModel
    vpd.OPERATION=conf.Operation
    vpd.TOPIC_UPDATERECIPE = conf.DeviceID+"/loadRecipe";
    vpd.TOPIC_UPDATESTATUS = conf.DeviceID+"/status";
    vpd.TOPIC_UPDATEDATA = conf.DeviceID+"/updatedata";
    vpd.TOPIC_PUB_TAKEPICTURE = conf.DeviceID+"/req_takepicture";
    vpd.TOPIC_SUB_TAKEPICTURE = conf.DeviceID+"/ret_takepicture";
    vpd.TOPIC_REBOOT = conf.DeviceID+"/reboot";
    vpd.UPDATEDATE = datetime.now()
    db.commit()
    db.refresh(vpd)
    response.status_code = status.HTTP_201_CREATED
    return { 'msg' : 'Updated' }

