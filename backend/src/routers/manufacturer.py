# backend/src/routers/manufacturer.py
from fastapi import APIRouter, Depends, HTTPException
from ..core.database import get_db
from ..core.exc import DuplicateEntryError
from ..core.security.access import require_programmer, require_tech_lead
from ..schemas.manufacturer import CreateManufacturer, GetManufacturer, GetManufacturers
from ..services.manufacturers import ManufacturerService
from uuid import UUID
manufacturer_router = APIRouter(tags=["manufacturer"])


@manufacturer_router.post("/api/manufacturers", response_model=GetManufacturer)
async def post_add_manufacturer(
    manufacturer: CreateManufacturer,
    db=Depends(get_db),
    current_user=Depends(require_tech_lead)
):
    try:
        man_service = ManufacturerService(db)
        created_manufacturer = await man_service.add_manufacturer(manufacturer)
        return created_manufacturer

    except DuplicateEntryError as e:
        raise HTTPException(409, detail=str(e))

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        raise HTTPException(500, detail=str(e))


@manufacturer_router.get("/api/manufacturers", response_model=GetManufacturers)
async def rest_get_manufacturers(
    db=Depends(get_db), current_user=Depends(require_programmer)
):
    man_service = ManufacturerService(db)
    manufacturers = await man_service.get_manufacturers()
    return GetManufacturers(manufacturers=manufacturers)


@manufacturer_router.delete("/api/manufacturers/{manufacturer_id}")
async def delete_manufacturers(manufacturer_id: str, current_user=Depends(require_tech_lead), db=Depends(get_db)):
    man_service = ManufacturerService(db)
    await man_service.delete_manufacturer(manufacturer_id)
    return None
