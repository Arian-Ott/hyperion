# Hyperion
# Copyright (C) 2025 Arian Ott <arian.ott@ieee.org>

from typing import Optional, Sequence, Any, Annotated
from pydantic import BaseModel, ConfigDict, BeforeValidator, UUID7


class CreateManufacturer(BaseModel):
    name: str 
    website: str


class GetManufacturer(BaseModel):
    id:UUID7

    name: str

    website: str
    model_config = ConfigDict(from_attributes=True)


class GetManufacturers(BaseModel):
    manufacturers: Sequence[GetManufacturer]
