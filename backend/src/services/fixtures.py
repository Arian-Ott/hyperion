from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from ..schemas.manufacturer import CreateManufacturer
from ..models.shows import  Manufacturer

class FixtureService:
    
    def __init__(self, session:AsyncSession):
        self.db = session
        
    async def add_manufacturer(self, create_manufacturer:CreateManufacturer ):
        try:
            manufacturer = Manufacturer(
                short_name=create_manufacturer.short_name,
                name=create_manufacturer.name
            )
            self.db.add(manufacturer)
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            