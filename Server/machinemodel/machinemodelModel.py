# coding: utf-8
from pydantic import BaseModel, Field


class VPDmodelbasemodel(BaseModel):
    MACHINE_TYPE: str
    CREATEDATE: str


class VPDmodelbase(BaseModel):
    MACHINE_TYPE: str = Field(..., example="xxxx")
    class Config:
        orm_mode = True




