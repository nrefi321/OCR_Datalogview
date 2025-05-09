
from pydantic import BaseModel
class VPDAlarm(BaseModel):
    MachineNo: str
    MachineModel: str
    Operation: str
    DeviceID: str
    AlarmDetail: str
    # CREATEDATE :str
