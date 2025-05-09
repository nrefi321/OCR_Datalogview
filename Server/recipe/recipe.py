from datetime import datetime, date

from fastapi import APIRouter, Depends ,Response ,status
from pydantic import BaseModel
from typing import Optional, List

from sqlalchemy import and_
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

from .dbrecipe import session,VPDrecipe,VPDlastrecipe
from .recipeModel import VPDrecc,VPDlastrec,VPDlastrecc,VPDModelLast
import json
from pydantic.datetime_parse import datetime


recipe = APIRouter(
    prefix="/Recipe",
    tags=["Recipe"],
    responses={404: {"message": "Not found"}}
)

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

@recipe.get("/LastRecipe",status_code=200)
async def GetLastRecipe(response: Response,db:session = Depends(get_db)):
    data = db.query(VPDlastrecipe.DEVICE_ID,VPDlastrecipe.LASTRECIPE).distinct().filter(VPDlastrecipe.ACTIVEFLAG == True).all()
    if(len(data)==0):
        response.status_code = 404
        return {'msg':'No Data'}
    res = {}
    for i in data:
        key = i.DEVICE_ID
        try:
            if(len(res[key])>0):
                pass
            else:
                res[key] = []
        except:
            res[key] = [] 
        res[key]= i.LASTRECIPE
        response.status_code = status.HTTP_200_OK
    return res

@recipe.get("/LastRecipe/{DeviceID}",status_code=200)
async def GetLastRecipe(DeviceID:str,response: Response ,db:session = Depends(get_db)):
    data = db.query(
        VPDlastrecipe.DEVICE_ID,
        VPDlastrecipe.LASTRECIPE
        ).distinct().filter(and_(
            VPDlastrecipe.ACTIVEFLAG == True,
            VPDlastrecipe.DEVICE_ID == DeviceID)).all()
    if(len(data)==0):
        response.status_code = 404
        return {'msg':'No Data'}
    res = {}
    for i in data:
        key = i.DEVICE_ID
        try:
            if(len(res[key])>0):
                pass
            else:
                res[key] = []
        except:
            res[key] = [] 
        res[key]= i.LASTRECIPE
        response.status_code = status.HTTP_200_OK
    return res

@recipe.post("/LastRecipe",status_code=201)
async def PostLastRecipe(response: Response,vpdrequest: VPDlastrecc, db:session = Depends(get_db)):
    data = db.query(VPDlastrecipe).filter(and_(VPDlastrecipe.ACTIVEFLAG == True,VPDlastrecipe.DEVICE_ID == vpdrequest.DEVICE_ID)).first()
    if(data is not None):
        print(vpdrequest.LASTRECIPE)
        data.LASTRECIPE = vpdrequest.LASTRECIPE
        data.LASTUPDATE = datetime.now()
        db.commit()
        db.refresh(data)
        response.status_code = status.HTTP_201_CREATED
        return { 'msg' : 'Updated' }
    else:
        data2 = VPDlastrecipe()
        data2.DEVICE_ID = vpdrequest.DEVICE_ID
        data2.LASTRECIPE = vpdrequest.LASTRECIPE
        data2.LASTUPDATE = datetime.now()
        db.add(data2)
        db.commit()
        response.status_code = status.HTTP_201_CREATED
        return { 'msg':'Created' }

@recipe.put('/LastRecipe/{DeviceID}',status_code=201)
async def PutLastRecipe(DeviceID:str,response: Response,LastRecipe:VPDModelLast,db:Session=Depends(get_db)):
    vpd = db.query(VPDlastrecipe).filter(and_(VPDlastrecipe.DEVICE_ID == DeviceID,VPDlastrecipe.ACTIVEFLAG == True)).first()
    if(vpd is None):
        response.status_code = 404
        return {'msg':'No Data'}
    vpd.LASTRECIPE = LastRecipe.LASTRECIPE
    vpd.LASTUPDATE = datetime.now()
    db.commit()
    db.refresh(vpd)
    response.status_code = status.HTTP_201_CREATED
    return {'msg':'Updated'}


@recipe.get("/LoadRecipe",status_code=200)
async def GetAllRecipeName(response: Response,db:session = Depends(get_db)):
    allRecipe = db.query(VPDrecipe.RECIPENAME).distinct().filter(VPDrecipe.ACTIVEFLAG == True).all()
    data = []
    for i in allRecipe:
        data.append(i.RECIPENAME)
    res = {'AllRecipe' : data }
    return res

@recipe.get("/LoadRecipe/{RecipeName}",status_code=200)
async def GetRecipe(RecipeName: str, response: Response,db:session = Depends(get_db)):
    data = db.query(VPDrecipe.RECIPEDETAIL).distinct().filter(and_(VPDrecipe.RECIPENAME == RecipeName,VPDrecipe.ACTIVEFLAG == True)).first()
    response.status_code = status.HTTP_200_OK
    return json.loads(data.RECIPEDETAIL)

@recipe.post("/LoadRecipe",status_code=201)
async def PostRecipe(response: Response,vpdrequest: VPDrecc, db:session = Depends(get_db)):
    data = db.query(VPDrecipe).filter(and_(VPDrecipe.ACTIVEFLAG == True,VPDrecipe.RECIPENAME == vpdrequest.RECIPENAME)).first()
    if(data is not None):
        data.RECIPEDETAIL = vpdrequest.RECIPEDETAIL
        data.CREATEDATE = data.CREATEDATE 
        data.UPDATEDATE = datetime.now()
        #print(data.CREATEDATE)
        #print(data.UPDATEDATE)
        db.add(data)
        db.commit()
        db.refresh(data)
        response.status_code = status.HTTP_201_CREATED
        return { 'msg' : 'Updated' }
    else:
        VPD = VPDrecipe()
        VPD.RECIPENAME = vpdrequest.RECIPENAME
        VPD.RECIPEDETAIL = vpdrequest.RECIPEDETAIL
        VPD.CREATEDATE = datetime.now()
        db.add(VPD)
        db.commit()
        response.status_code = status.HTTP_201_CREATED
        return { 'msg': 'Created' }
