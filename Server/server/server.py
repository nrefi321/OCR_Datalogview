from datetime import datetime, date

from fastapi import APIRouter, Depends , Response ,status
from pydantic import BaseModel
from typing import Optional, List

from sqlalchemy import and_
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

from .dbserver import session,sessioninsert
from .serverModel import VPDserv,VPDserver,VPDservv


server = APIRouter(
    prefix="/ServerConfig",
    tags=["ServerConfig"],
    responses={200: {"message": "OK"}}
)

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()
        
def get_db2():
    db = sessioninsert()
    try:
        yield db
    finally:
        db.close()


@server.get("/",status_code=200)
def VPD_Server(response: Response):
    vpdss = session.query(VPDserver.SERVER,VPDserver.MQTT_BROKER).first()
    response.status_code = status.HTTP_200_OK
    return vpdss

@server.put('/',status_code=200)
async def update_users(response: Response,conf:VPDservv,db:Session=Depends(get_db2)):
    vpd = db.query(VPDserver).first()
    vpd.MQTT_BROKER=conf.MQTT_BROKER
    vpd.SERVER=conf.SERVER
    db.commit()
    db.refresh(vpd)
    response.status_code = status.HTTP_201_CREATED
    return { 'msg': 'Updated' }