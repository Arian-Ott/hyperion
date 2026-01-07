from ..show import CreateShow, DeleteShow
from pydantic import BaseModel

class ShowRequest(BaseModel):
    cmd:str
    data:CreateShow
    
class ShowDeleteRequest(BaseModel):
    cmd:str
    data: DeleteShow