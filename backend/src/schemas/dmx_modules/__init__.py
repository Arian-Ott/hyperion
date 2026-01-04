from pydantic import BaseModel


class AbstractBaseCommand(BaseModel):
    cmd: str
    data: BaseModel
