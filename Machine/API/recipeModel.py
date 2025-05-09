# coding: utf-8
from pydantic import BaseModel, Field


class VPDlastrecc(BaseModel):
    DEVICE_ID : str = Field(..., example="vpdxx")
    LASTRECIPE : str = Field(..., example="AGP/TNF")
    
class VPDModelLast(BaseModel):
    LASTRECIPE : str

class VPDlastrec(BaseModel):
    ITEM : int
    DEVICE_ID : str
    LASTRECIPE : str
    LASTUPDATE : str

class VPDrecc(BaseModel):
    RECIPENAME : str
    RECIPEDETAIL : str
