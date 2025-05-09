from sqlalchemy import create_engine,Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic.datetime_parse import datetime

host="10.151.17.2"
user="vpd"
password="vpd"

engine = create_engine('mysql://{}:{}@{}/vpd_system'.format(user, password, host),echo = False)
session = sessionmaker(bind = engine)
Base = declarative_base()

class VPDlastrecipe(Base):
    __tablename__ = 'vpdlastrecipe'
    ITEM = Column(Integer, primary_key=True, autoincrement=True)
    DEVICE_ID = Column(String(20))
    LASTRECIPE = Column(String(20))
    LASTUPDATE= Column('LASTUPDATE', TIMESTAMP(timezone=False), nullable=False, default=datetime.now())
    ACTIVEFLAG = Column(Boolean, default=True)

class VPDrecipe(Base):
    __tablename__ = 'vpdrecipe'
    ITEM = Column(Integer, primary_key=True, autoincrement=True)
    RECIPENAME = Column(String(20))
    RECIPEDETAIL = Column(String(4294000000))
    CREATEDATE = Column('CREATEDATE', TIMESTAMP(timezone=False), nullable=False, default=datetime.now())
    UPDATEDATE= Column('UPDATEDATE', TIMESTAMP(timezone=False), nullable=False, default=datetime.now())
    ACTIVEFLAG = Column(Boolean, default=True)

Base.metadata.create_all(engine)