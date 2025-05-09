# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

host="127.0.0.1"
user="vpd"
password="vpd"

DATABASE = "mysql://{}:{}@{}/vpd_system".format(user, password, host)


ENGINE = create_engine(
    DATABASE,
    encoding="utf-8",
    echo=True
)

session = scoped_session(
    sessionmaker(
        autocommit=True,
        autoflush=True,
        bind=ENGINE
    )
)

sessioninsert = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=True,
        bind=ENGINE
    )
)


Base = declarative_base()
Base.query = session.query_property()
