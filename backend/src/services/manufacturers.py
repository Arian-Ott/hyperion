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
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from ..core.exc import DuplicateEntryError
from ..schemas.manufacturer import CreateManufacturer, GetManufacturers, GetManufacturer
from ..models.fixtures import Manufacturer
import uuid

class ManufacturerService:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def add_manufacturer(self, create_manufacturer: CreateManufacturer):
        try:
            manufacturer = Manufacturer(
                name=create_manufacturer.name, website=create_manufacturer.website
            )
            self.db.add(manufacturer)
            await self.db.flush()
            await self.db.commit()
            print(manufacturer.id)
            return manufacturer
        except IntegrityError:
            await self.db.rollback()
            raise DuplicateEntryError(f"Manufacturer '{create_manufacturer.name}' already exists.")


    async def get_manufacturers(self):

        qry = select(Manufacturer)

        result = await self.db.execute(qry)

        manufacturers = result.scalars().all()

        return manufacturers


    async def delete_manufacturer(self, manufacturer_id):
        # 1. Validierung der UUID

        # 2. Objekt laden (Wichtig für SQLAlchemy Session State)
        # Wir holen den Hersteller. Wir müssen die Kinder NICHT laden,
        print(manufacturer_id)
        stmt = select(Manufacturer).where(Manufacturer.id == uuid.UUID(manufacturer_id))
        result = await self.db.execute(stmt)
        manufacturer = result.scalar_one_or_none()

        if not manufacturer:
            print("YIKES")
            raise HTTPException(
                status_code=404, detail="Manufacturer not found")

        # 3. Löschen
        try:
            await self.db.delete(manufacturer)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            # Falls immer noch Fehler auftreten, sehen wir hier genau was los ist
            print(f"DEBUG ERROR: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Database error during deletion: {str(e)}"
            )
