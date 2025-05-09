from sqlalchemy import create_engine,Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic.datetime_parse import datetime

host="127.0.0.1"
user="vpd"
password="vpd"
engine = create_engine('mysql://{}:{}@{}/vpd_result'.format(user, password, host),echo = False)
session = sessionmaker(bind = engine)
#session = Session()
Base = declarative_base()
class VPDresult(Base):
    __tablename__ = 'alarmresult'
    ITEM = Column(Integer, primary_key=True, autoincrement=True)
    MACHINE_NO = Column(String(20))
    MACHINE_MODEL = Column(String(20))
    OPERATION = Column(String(20))
    DEVICE_ID = Column(String(20))
    ALARM_DETAIL = Column(String(4294000000))
    CREATEDATE = Column('CREATEDATE', TIMESTAMP(timezone=False), nullable=False, default=datetime.now())
    ACTIVEFLAG = Column(Boolean, default=True)
Base.metadata.create_all(engine)