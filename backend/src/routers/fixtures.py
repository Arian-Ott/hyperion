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

from fastapi import APIRouter, Depends, status, HTTPException
from ..schemas.fixtures import CreateFixtureType, CreateFixturePatch
from ..services.fixture_service import FixtureService
from ..core.database import get_db
from ..core.security.access import require_tech_lead

fixture_router = APIRouter(tags=["fixtures"])


@fixture_router.post("/api/fixture-types")
async def post_add_fixture(
    new_fixture: CreateFixtureType,
    db=Depends(get_db),
    current_user=Depends(require_tech_lead),
):
    fixture_service = FixtureService(db)
    fixture = await fixture_service.create_fixture_type(new_fixture)
    return fixture


@fixture_router.post("/api/fixture")
async def patch_fixture_endpoint(patch_data: CreateFixturePatch, db=Depends(get_db)):
    service = FixtureService(db)
    try:
        return await service.patch_fixture(patch_data)
    except ValueError as e:
        # Wir wandeln unsere Logik-Fehler in saubere HTTP 400 Errors um
        raise HTTPException(status_code=400, detail=str(e))
