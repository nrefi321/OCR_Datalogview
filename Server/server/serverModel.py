# coding: utf-8
from pydantic.datetime_parse import datetime
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from pydantic import BaseModel, Field
from .dbserver import Base
from .dbserver import ENGINE
import uvicorn

class VPDserver(Base):
    __tablename__ = 'vpdserver'
    ITEM = Column(Integer, primary_key=True, autoincrement=True)
    MQTT_BROKER = Column(String)
    SERVER = Column(String)
    UPDATEDATE = Column('UPDATEDATE', TIMESTAMP(timezone=False), nullable=False, default=datetime.now())
    ACTIVEFLAG = Column(Boolean, default=True)


class VPDservv(BaseModel):
    MQTT_BROKER : str
    SERVER : str


class VPDserv(BaseModel):
    ITEM : int
    MQTT_BROKER : str
    SERVER : str
    UPDATEDATE : str
    ACTIVEFLAG : bool

    class Config:
        orm_mode = True
