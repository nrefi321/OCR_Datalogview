from sqlalchemy import create_engine,Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic.datetime_parse import datetime

host="127.0.0.1"
user="vpd"
password="vpd"

engine = create_engine('mysql://{}:{}@{}/vpd_system'.format(user, password, host),echo = False)
session = sessionmaker(bind = engine)
Base = declarative_base()

class VPDmodel(Base):
    __tablename__ = 'vpdmodel'
    ITEM = Column(Integer, primary_key=True, autoincrement=True)
    MACHINE_TYPE = Column(String(20))
    CREATEDATE= Column('CREATEDATE', TIMESTAMP(timezone=False), nullable=False, default=datetime.now())
    ACTIVEFLAG = Column(Boolean, default=True,autoincrement=True)

Base.metadata.create_all(engine)
