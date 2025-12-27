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

from fastapi import APIRouter, Depends
from ..core.database import get_db
from ..core.security.access import require_tech_lead
from ..schemas.manufacturer import CreateManufacturer, GetManufacturer
from ..services.manufacturers import ManufacturerService
manufacturer_router = APIRouter(tags=["manufacturer"])


@manufacturer_router.post("/api/manufacturers")
async def post_add_manufacturer(manufacturer: CreateManufacturer, db=Depends(get_db), current_user=Depends(require_tech_lead)):
    man_service = ManufacturerService(db)
    created_manufacturer = await man_service.add_manufacturer(manufacturer)

    return GetManufacturer(id=created_manufacturer.id, name=created_manufacturer.name, website=created_manufacturer.website)


@manufacturer_router.get("/api/manufacturers")
async def get_manufacturers(db=Depends(get_db), current_user=Depends(require_tech_lead)):
    man_service = ManufacturerService(db)
    manufacturers = await man_service.get_manufacturers()
    return manufacturers
