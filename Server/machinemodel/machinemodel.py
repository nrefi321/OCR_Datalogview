from datetime import datetime, date

from fastapi import APIRouter, Depends ,Response ,status
from pydantic import BaseModel
from typing import Optional, List

from sqlalchemy import and_, asc
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

from .dbmachine import session,VPDmodel
from .machinemodelModel import VPDmodelbase,VPDmodelbasemodel
import json
from pydantic.datetime_parse import datetime


Machinemodel = APIRouter(
    prefix="/MachineModel",
    tags=["MacineModel"],
    responses={404: {"message": "Not found"}}
)

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

@Machinemodel.get("/",status_code=200)
async def GetModel(response: Response,db:session = Depends(get_db)):
    data = db.query(VPDmodel).filter(and_(VPDmodel.ACTIVEFLAG == True)).order_by(asc(VPDmodel.MACHINE_TYPE)).all()
    if(data is None):
        response.status_code = 404
        return {'msg':'No Data'}
    res = []
    for i in data:
        res.append(i.MACHINE_TYPE)
    response.status_code = status.HTTP_200_OK
    return res


@Machinemodel.post("/UpdateMachine_model",status_code=201)
async def UpdateMachineModel(response: Response,vpdrequest: VPDmodelbase, backgroundtask: BackgroundTasks, db:session = Depends(get_db)):
    data = db.query(VPDmodel).filter(VPDmodel.MACHINE_TYPE == vpdrequest.MACHINE_TYPE).first()
    if(data is not None):
        data.MACHINE_TYPE=vpdrequest.MACHINE_TYPE
        data.UPDATEDATE = datetime.now()
        db.commit()
        db.refresh(data)
        response.status_code = status.HTTP_201_CREATED
        return { 'msg' : 'Updated' }
    else:
        VPD = VPDmodel()
        VPD.MACHINE_TYPE = vpdrequest.MACHINE_TYPE
        VPD.UPDATEDATE = datetime.now()
        db.add(VPD)
        db.commit()
        response.status_code = status.HTTP_201_CREATED
        return { 'msg':'Created'}