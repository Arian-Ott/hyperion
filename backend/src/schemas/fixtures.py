# Hyperion
# Copyright (C) 2025 Arian Ott <arian.ott@ieee.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from pydantic import BaseModel, UUID7, Field
from ..models.fixtures import AttributeType
from typing import List


class FixtureChannelCreate(BaseModel):
    dmx_offset: int = Field(..., ge=1)
    attribute: AttributeType
    default_value: int = 0
    highlight_value: int = 255
    invert_default: bool = False


class CreateFixtureType(BaseModel):
    manufacturer_id: str  # oder UUID
    model: str
    mode_name: str
    channels: List[FixtureChannelCreate]  # <--- Diese Liste wird oben iteriert


class CreateFixturePatch(BaseModel):
    show_id: UUID7
    fixture_type_id: UUID7
    name: str
    fid: int = Field(..., description="User ID like 101")
    universe: int = Field(0, ge=0)
    start_address: int = Field(..., ge=1, le=512)
    invert_pan: bool = False
    invert_tilt: bool = False
