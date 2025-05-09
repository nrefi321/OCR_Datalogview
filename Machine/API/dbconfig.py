from sqlalchemy import create_engine,Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic.datetime_parse import datetime

host="127.0.0.1"
user="vpd"
password="vpd"

engine = create_engine('mysql://{}:{}@{}/vpd_system'.format(user, password, host),echo = False)
session = sessionmaker(bind = engine)
#session = Session()
Base = declarative_base()

class VPDconfig(Base):
    __tablename__ = 'vpdconfig'
    ITEM = Column(Integer, primary_key=True, autoincrement=True)
    DEVICE_ID = Column(String(20),index = True)
    DEVICE_IP = Column(String(20))
    MACHINE_NO = Column(String(20))
    MACHINE_MODEL = Column(String(20))
    OPERATION = Column(String(20))
    TOPIC_UPDATERECIPE = Column(String(20))
    TOPIC_UPDATESTATUS = Column(String(20))
    TOPIC_UPDATEDATA = Column(String(20))
    TOPIC_PUB_TAKEPICTURE = Column(String(20))
    TOPIC_SUB_TAKEPICTURE = Column(String(20))
    TOPIC_REBOOT = Column(String(20))
    UPDATEDATE = Column('UPDATEDATE', TIMESTAMP(timezone=False), nullable=False, default=datetime.now())
    ACTIVEFLAG = Column(Boolean, default=True,autoincrement=True)

#database migration
Base.metadata.create_all(engine)
