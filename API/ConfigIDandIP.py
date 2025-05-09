from fastapi import FastAPI
import json
from fastapi.encoders import jsonable_encoder
import os
import uvicorn
from fastapi import Depends , Response , status
from pydantic import BaseModel
from sqlalchemy import and_,desc,asc
from dbconfig import session,VPDconfig
from configModel import VPDconff,VPDconf,VPDConfigModel
from pydantic.datetime_parse import datetime
from dbrecipe import session,VPDrecipe,VPDlastrecipe
from recipeModel import VPDlastrecc


app = FastAPI(
    title="CONFIG DEVICE ID and IP",
    description="EDIT CONFIC BELOW",
    version="1.0.0"
)

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
engine = create_engine('sqlite:///college.db', echo = True)
meta = MetaData()

DeviceIDandIP = '/home/vpd/MoldDataLogviewJetson/VPDDatalog/VPDConfig/config/deviceIDandIP.json'
server = '/home/vpd/MoldDataLogviewJetson/VPDDatalog/VPDConfig/config/server.json'
# DeviceIDandIP = 'C:\\Users\\41411046\Desktop\\VPD-installationGuide\\MoldDataLogviewJetson\\VPDDatalog\\VPDConfig\\config\\deviceIDandIP.json'
# server = 'C:\\Users\\41411046\\Desktop\\VPD-installationGuide\\MoldDataLogviewJetson\\VPDDatalog\\VPDConfig\\config\\server.json'


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

class DEVICEmodel(BaseModel):
    DEVICE_ID: str

class SERVERmodel(BaseModel):
    Server: str
    MQTTBroker: str

class reboot(BaseModel):
    reboot: str

@app.get("/getDevice",response_model=DEVICEmodel)
async def getDevice():
    param = []
    # with open(r'C:\Users\41411046\Desktop\VPD-installationGuide\MoldDataLogviewJetson\VPDDatalog\VPDConfig\config\deviceIDandIP.json') as file:
    with open(DeviceIDandIP, 'r+') as f:
        param = json.load(f)
    return param


@app.put("/Update_Device_Name",status_code=201)
async def Update_Device_Name(Device_name: str,Device_IP:str,Machine_No: str,MachineModel:str,Operation:str,response: Response,
                             vpdrequest: VPDconf,vpdrequest_recipe: VPDlastrecc,db: session = Depends(get_db)):
    data = []
    # filename = 'C:\\Users\\41411046\Desktop\\VPD-installationGuide\\MoldDataLogviewJetson\\VPDDatalog\\VPDConfig\\config\\deviceIDandIP.json'
    with open(DeviceIDandIP, 'r+') as f:
        data = json.load(f)
        data['DEVICE_ID'] = jsonable_encoder(Device_name)  # <--- add `id` value.
        data['DEVICE_IP'] = jsonable_encoder(Device_IP)  # <--- add `id` value.
        f.seek(0)  # <--- should reset file position to the beginning.
        json.dump(data, f, indent=4)
        f.truncate()  # remove remaining part

        vpdrequest.DeviceID = Device_name
        vpdrequest.DeviceIP = Device_IP
        vpdrequest.MachineNo = Machine_No
        vpdrequest.MachineModel = MachineModel
        vpdrequest.Operation = Operation

        datacheck = db.query(VPDconfig).filter(VPDconfig.DEVICE_ID == vpdrequest.DeviceID).first()
        if (datacheck is not None):
            datacheck.DEVICE_ID = vpdrequest.DeviceID
            datacheck.DEVICE_IP = vpdrequest.DeviceIP
            datacheck.MACHINE_NO = vpdrequest.MachineNo
            datacheck.MACHINE_MODEL = vpdrequest.MachineModel
            datacheck.OPERATION = vpdrequest.Operation
            datacheck.TOPIC_UPDATERECIPE = vpdrequest.DeviceID + "/loadRecipe"
            datacheck.TOPIC_UPDATESTATUS = vpdrequest.DeviceID + "/status"
            datacheck.TOPIC_UPDATEDATA = vpdrequest.DeviceID + "/updatedata"
            datacheck.TOPIC_PUB_TAKEPICTURE = vpdrequest.DeviceID + "/req_takepicture"
            datacheck.TOPIC_SUB_TAKEPICTURE = vpdrequest.DeviceID + "/ret_takepicture"
            datacheck.TOPIC_REBOOT = vpdrequest.DeviceID + "/reboot"
            datacheck.UPDATEDATE = datetime.now()
            db.commit()
            db.refresh(datacheck)
            response.status_code = status.HTTP_201_CREATED
            return {'msg': 'Updated'}
        else:
            VPD = VPDconfig()
            VPD.DEVICE_ID = vpdrequest.DeviceID
            VPD.DEVICE_IP = vpdrequest.DeviceIP
            VPD.MACHINE_NO = vpdrequest.MachineNo
            VPD.MACHINE_MODEL = vpdrequest.MachineModel
            VPD.OPERATION = vpdrequest.Operation
            VPD.TOPIC_UPDATERECIPE = vpdrequest.DeviceID + "/loadRecipe"
            VPD.TOPIC_UPDATESTATUS = vpdrequest.DeviceID + "/status"
            VPD.TOPIC_UPDATEDATA = vpdrequest.DeviceID + "/updatedata"
            VPD.TOPIC_PUB_TAKEPICTURE = vpdrequest.DeviceID + "/req_takepicture"
            VPD.TOPIC_SUB_TAKEPICTURE = vpdrequest.DeviceID + "/ret_takepicture"
            VPD.TOPIC_REBOOT = vpdrequest.DeviceID + "/reboot"
            VPD.UPDATEDATE = datetime.now()
            db.add(VPD)
            db.commit()
            response.status_code = status.HTTP_201_CREATED

        vpdrequest_recipe.DEVICE_ID = Device_name
        vpdrequest_recipe.LASTRECIPE = 'AGP'
        data = db.query(VPDlastrecipe).filter(and_(VPDlastrecipe.ACTIVEFLAG == True, VPDlastrecipe.DEVICE_ID == vpdrequest_recipe.DEVICE_ID)).first()
        if (data is not None):
            # print(vpdrequest.LASTRECIPE)
            data.LASTRECIPE = vpdrequest_recipe.LASTRECIPE
            data.LASTUPDATE = datetime.now()
            db.commit()
            db.refresh(data)
            response.status_code = status.HTTP_201_CREATED
            return {'msg': 'Updated'}
        else:
            data2 = VPDlastrecipe()
            data2.DEVICE_ID = vpdrequest_recipe.DEVICE_ID
            data2.LASTRECIPE = vpdrequest_recipe.LASTRECIPE
            data2.LASTUPDATE = datetime.now()
            db.add(data2)
            db.commit()
            response.status_code = status.HTTP_201_CREATED
                # return {'msg': 'Created'}

    return {'msg': 'Created'}

    # return data

@app.get("/Server",response_model=SERVERmodel)
async def getServer():
    param = []
    # with open(r'C:\Users\41411046\Desktop\VPD-installationGuide\MoldDataLogviewJetson\VPDDatalog\VPDConfig\config\deviceIDandIP.json') as file:
    with open(server, 'r+') as f:
        param = json.load(f)
    return param

@app.put("/Updateserver",response_model=SERVERmodel)
async def Update_Server(SERVER: str,MQTTBroker: str):
    data = []
    # filename = 'C:\\Users\\41411046\Desktop\\VPD-installationGuide\\MoldDataLogviewJetson\\VPDDatalog\\VPDConfig\\config\\deviceIDandIP.json'
    with open(server, 'r+') as f:
        data = json.load(f)
        data['Server'] = jsonable_encoder(SERVER)  # <--- add `id` value.
        data['MQTTBroker'] = jsonable_encoder(MQTTBroker)  # <--- add `id` value.
        f.seek(0)  # <--- should reset file position to the beginning.
        json.dump(data, f, indent=4)
        f.truncate()  # remove remaining part
    return data


@app.get("/Reboot")
async def Reboot_now():
    message = 'reboot'
    os.popen("sudo -S %s" % ('reboot'), 'w').write('vpd\n')
    return message

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

# //172.16.42.104



# os.popen("sudo -S %s"%('reboot'), 'w').write('vpd\n')
