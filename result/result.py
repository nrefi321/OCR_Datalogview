from datetime import datetime,date
from fastapi import FastAPI, requests , Depends , Response ,status ,APIRouter
from typing import List

from sqlalchemy import and_,desc,asc
from starlette.background import BackgroundTasks
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse

from .resultdb import session,VPDresult
from .resultModel import VPDAlarm

from pydantic.datetime_parse import datetime

result = APIRouter(
    prefix="/AlarmData",
    tags=["Result"],
    responses={200: {"message": "OK"}}
)


def get_db():
    try:
        db = session()
        yield db
    finally:
        db.close()

@result.get("/ByMachine")
async def AlarmByMachine(db:session = Depends(get_db)):
    vpd = db.query(VPDresult).filter(and_(VPDresult.ACTIVEFLAG == True,VPDresult.MACHINE_NO.isnot(None))).order_by(asc(VPDresult.MACHINE_NO)).all()
    res = {}
    for i in vpd:
        key = i.MACHINE_NO
        try:
            if(len(res[key])>0):
                pass
            else:
                res[key] = []
        except:
            res[key] = []
            
        resdic = {}
        resdic['MachineModel'] = i.MACHINE_MODEL
        resdic['Operation'] = i.OPERATION
        resdic['DeviceID'] = i.DEVICE_ID
        resdic['AlarmDetail'] = i.ALARM_DETAIL
        resdic['CreateDate'] = i.CREATEDATE
        res[key].append(resdic)
    return res

@result.get("/ByMachine/{MachineNo}")
async def AlarmByMachine(MachineNo,db:session = Depends(get_db)):
    vpd = db.query(VPDresult).filter(and_(VPDresult.ACTIVEFLAG == True,VPDresult.MACHINE_NO == MachineNo)).order_by(asc(VPDresult.MACHINE_NO)).all()
    res = {}
    for i in vpd:
        key = i.MACHINE_NO
        try:
            if(len(res[key])>0):
                pass
            else:
                res[key] = []
        except:
            res[key] = []
            
        resdic = {}
        resdic['MachineModel'] = i.MACHINE_MODEL
        resdic['Operation'] = i.OPERATION
        resdic['DeviceID'] = i.DEVICE_ID
        resdic['AlarmDetail'] = i.ALARM_DETAIL
        resdic['CreateDate'] = i.CREATEDATE
        res[key].append(resdic)
    return res

@result.get("/ByDevice")
async def AlarmByDevice(db:session = Depends(get_db)):
    vpd = db.query(VPDresult).filter(and_(VPDresult.ACTIVEFLAG == True,VPDresult.DEVICE_ID.isnot(None))).order_by(asc(VPDresult.DEVICE_ID)).all()
    res = {}
    for i in vpd:
        key = i.DEVICE_ID
        try:
            if(len(res[key])>0):
                pass
            else:
                res[key] = []
        except:
            res[key] = []
            
        resdic = {}
        resdic['MachineNo'] = i.MACHINE_NO
        resdic['MachineModel'] = i.MACHINE_MODEL
        resdic['Operation'] = i.OPERATION
        resdic['AlarmDetail'] = i.ALARM_DETAIL
        resdic['CreateDate'] = i.CREATEDATE
        res[key].append(resdic)
    return res 

@result.get("/ByDevice/{DeviceID}")
async def AlarmByDevice(DeviceID,db:session = Depends(get_db)):
    vpd = db.query(VPDresult).filter(and_(VPDresult.ACTIVEFLAG == True,VPDresult.DEVICE_ID == DeviceID)).order_by(asc(VPDresult.DEVICE_ID)).all()
    res = {}
    for i in vpd:
        key = i.DEVICE_ID
        try:
            if(len(res[key])>0):
                pass
            else:
                res[key] = []
        except:
            res[key] = []
            
        resdic = {}
        resdic['MachineNo'] = i.MACHINE_NO
        resdic['MachineModel'] = i.MACHINE_MODEL
        resdic['Operation'] = i.OPERATION
        resdic['AlarmDetail'] = i.ALARM_DETAIL
        resdic['CreateDate'] = i.CREATEDATE
        res[key].append(resdic)
    return res

@result.get("/ByDate/{FromDate}&{ToDate}")
async def AlarmByDate(FromDate:date, ToDate: date,db:session = Depends(get_db)):
    fromdatestr = str(FromDate)+' 00:00:00'
    todatestr = str(ToDate)+' 23:59:59'
    data = db.query(VPDresult).filter(and_(VPDresult.CREATEDATE.between(fromdatestr, todatestr),VPDresult.ACTIVEFLAG == True)).all()
    res = {}
    for i in data:
        key = i.MACHINE_NO
        try:
            if(len(res[key])>0):
                pass
            else:
                res[key] = []
        except:
            res[key] = []
        resdic = {}
        resdic['DeviceID'] = i.DEVICE_ID
        resdic['MachineModel'] = i.MACHINE_MODEL
        resdic['Operation'] = i.OPERATION
        resdic['AlarmDetail'] = i.ALARM_DETAIL
        resdic['CreateDate'] = i.CREATEDATE
        res[key].append(resdic)
    return res

@result.get("/ByMachineDate/{MachineNo}&{FromDate}&{ToDate}")
async def AlarmByMachineDate(MachineNo,FromDate:date, ToDate: date,db:session = Depends(get_db)):
    fromdatestr = str(FromDate)+' 00:00:00'
    todatestr = str(ToDate)+' 23:59:59'
    data = db.query(VPDresult).filter(and_(VPDresult.CREATEDATE.between(fromdatestr, todatestr),VPDresult.MACHINE_NO == MachineNo,VPDresult.ACTIVEFLAG == True)).all()
    res = {}
    for i in data:
        key = i.MACHINE_NO
        try:
            if(len(res[key])>0):
                pass
            else:
                res[key] = []
        except:
            res[key] = []
        resdic = {}
        resdic['DeviceID'] = i.DEVICE_ID
        resdic['MachineModel'] = i.MACHINE_MODEL
        resdic['Operation'] = i.OPERATION
        resdic['AlarmDetail'] = i.ALARM_DETAIL
        resdic['CreateDate'] = i.CREATEDATE
        res[key].append(resdic)
    return res

@result.post("/")#, backgroundtask: BackgroundTasks, db:session = Depends(get_db2)
async def PostAlarmData(VPDdata: VPDAlarm,db:session = Depends(get_db)):

    VPD = VPDresult()
    VPD.MACHINE_NO = VPDdata.MachineNo
    VPD.MACHINE_MODEL = VPDdata.MachineModel
    VPD.OPERATION = VPDdata.Operation
    VPD.DEVICE_ID = VPDdata.DeviceID
    VPD.ALARM_DETAIL = VPDdata.AlarmDetail
    VPD.CREATEDATE = datetime.now()
    db.add(VPD)
    db.commit()
    return {"Code: Success"}

