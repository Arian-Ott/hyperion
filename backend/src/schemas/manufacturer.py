from pydantic import BaseModel


class CreateManufacturer(BaseModel):
    short_name: str
    name: str
