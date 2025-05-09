from fastapi import FastAPI
import json
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
import os
import uvicorn


app = FastAPI()

DeviceIDandIP = '/home/vpd/MoldDataLogviewJetson/VPDDatalog/VPDConfig/config/deviceIDandIP.json'
server = '/home/vpd/MoldDataLogviewJetson/VPDDatalog/VPDConfig/config/server.json'

@app.get("/")
async def configdata():
    param = []
    with open(DeviceIDandIP, 'r+') as f:
        param = json.load(f)
    return param


class DEVICEmodel(BaseModel):
    DEVICE_ID: str

class SERVERmodel(BaseModel):
    Server: str
    MQTTBroker: str

class reboot(BaseModel):
    reboot: str

@app.put("/UpdateDeviceID",response_model=DEVICEmodel)
async def update_DeviceID(DEVICE_ID: str):
    data = []
    with open(DeviceIDandIP, 'r+') as f:
        data = json.load(f)
        data['DEVICE_ID'] = jsonable_encoder(DEVICE_ID)  # <--- add `id` value.
        f.seek(0)  # <--- should reset file position to the beginning.
        json.dump(data, f, indent=4)
        f.truncate()  # remove remaining part
    return data

@app.get("/server")
async def serverdata():
    param = []
    with open(server, 'r+') as f:
        param = json.load(f)
    return param

@app.put("/Updateserver",response_model=SERVERmodel)
async def update_server(SERVER: str,MQTTBroker: str):
    data = []
    with open(server, 'r+') as f:
        data = json.load(f)
        data['Server'] = jsonable_encoder(SERVER)  # <--- add `id` value.
        data['MQTTBroker'] = jsonable_encoder(MQTTBroker)  # <--- add `id` value.
        f.seek(0)  # <--- should reset file position to the beginning.
        json.dump(data, f, indent=4)
        f.truncate()  # remove remaining part
    return data


@app.get("/reboot")
async def Rebootnow():
    message = 'reboot'
    os.popen("sudo -S %s" % ('reboot'), 'w').write('vpd\n')
    return message

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)



# os.popen("sudo -S %s"%('reboot'), 'w').write('vpd\n')
