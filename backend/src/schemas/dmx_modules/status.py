from pydantic import BaseModel
from . import AbstractBaseCommand
class Ping(BaseModel):
    ping:str
    
class PingRequest(AbstractBaseCommand):
    data:Ping