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
from ..schemas.manufacturer import CreateManufacturer
from ..models.shows import Manufacturer


class FixtureService:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def add_manufacturer(self, create_manufacturer: CreateManufacturer):
        try:
            manufacturer = Manufacturer(
                short_name=create_manufacturer.short_name, name=create_manufacturer.name
            )
            self.db.add(manufacturer)
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
