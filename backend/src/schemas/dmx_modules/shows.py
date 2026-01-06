from ..show import CreateShow
from pydantic import BaseModel

class ShowRequest(BaseModel):
    cmd:str
    data:CreateShow