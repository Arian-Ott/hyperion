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

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from ..schemas.manufacturer import CreateManufacturer, GetManufacturers, GetManufacturer
from ..models.fixtures import Manufacturer


class ManufacturerService:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def add_manufacturer(self, create_manufacturer: CreateManufacturer):
        try:
            manufacturer = Manufacturer(
                name=create_manufacturer.name, website=create_manufacturer.website
            )
            self.db.add(manufacturer)
            await self.db.commit()
            await self.db.refresh(manufacturer)
            return manufacturer       
        except IntegrityError:
            await self.db.rollback()
    
    async def get_manufacturers(self):
        qry = select(Manufacturer).union_all()
        manufacturers = await self.db.execute(qry)
        manufacturers = manufacturers.all()
        manufacturers = GetManufacturers(manufacturers=[GetManufacturer(id=str(x.id), name=x.name, website=x.website) for x in manufacturers])
        return manufacturers
    
