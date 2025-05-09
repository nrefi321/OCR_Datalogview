from fastapi import Depends, Response, status, APIRouter,UploadFile,File
import json 
import os
from typing import List

log_info = APIRouter(
    prefix="/log",
    tags=["LOG"],
    responses={200: {"message": "OK"}}
)

# mainpath = r'D:\fern\project_Fern\VPD_Mold\VPDlogfile'
mainpath = r'D:\VPDlogfile'

def save_file(mapname,filename, data):
    dir = os.path.join(mainpath,mapname)
    if not os.path.exists(dir):
        os.makedirs(dir)
    with open(os.path.join(mainpath,mapname,filename), 'wb') as f:
        f.write(data)


@log_info.post("_file")
async def LogInfo(response:Response,files: List[UploadFile] = File(...)):
    if(files is None):
        response.status_code = 400
        return {'msg':'Please upload log file'}
    filename = files[0].filename.strip()
    mapTrim = files[0].filename.strip().split('.')[-1]
    f1 = files[0].filename.strip().split('.')[1]
    # print(filename)
    # print(mapTrim)
    # print(f1)
    if(not (f1 == 'log' or f1 == 'png')):
        response.status_code = 400
        return {'msg':'Please upload 1 file image (png) and data (log)'}
    
    logFile = ''
    imgFile = ''
    for file in files:
        fnametrim = file.filename.strip()
        filetype = fnametrim.split('.')[1]
        if(not (filetype == 'log' or filetype == 'png')):
            response.status_code = 400
            return {'msg':'Please upload log and png file'}
        contents = await file.read()
        # fname = '{}.{}'.format(mapTrim,filetype)
        fname = filename
        save_file(mapTrim,fname, contents)
        if(filetype == 'log'):
            logFile = fname
        else:
            imgFile = fname

    print(logFile)
    print(imgFile)
    pathLog = os.path.join(mainpath,mapTrim,logFile)
    # pathImg = os.path.join(mainpath,mapTrim,imgFile)
    if(not (os.path.isfile(pathLog))):
        response.status_code = 500
        return {'msg':'Save file Error'}
    else:
        return {'msg': 'Uploaded'}
