from pydantic import BaseModel, Field
class VPDConfigModel(BaseModel):
    DeviceID :str 
    DeviceIP :str 
    MachineNo:str 
    MachineModel:str
    Operation:str
    Topic_UpdateRecipe:str
    Topic_UpdateStatus:str
    Topic_UpdateData:str
    Topic_Pub_TakePicture:str
    Topic_Sub_TakePicture:str
    
class VPDconff(BaseModel):
    DEVICE_ID : str
    DEVICE_IP : str
    MACHINE_NO : str
    MACHINE_MODEL : str
    OPERATION : str

class VPDconf(BaseModel):
    DeviceID : str = Field(..., example="vpdxx")
    DeviceIP : str = Field(..., example="127.0.0.1")
    MachineNo : str = Field(..., example="AGP-xxx")
    MachineModel : str = Field(..., example="GP-xxxxxxx")
    Operation : str = Field(..., example="Mold/TNF")
    class Config:
        orm_mode = True
