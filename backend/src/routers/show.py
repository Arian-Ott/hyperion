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

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from ..core.database import get_db
from ..core.security.access import require_operator, require_programmer
from ..core.exc import DuplicateEntryError
from ..schemas.show import (
    CreateFixturesInScene,
    CreateFixturesInSceneRequest,
    CreateScene,
    CreateShow,
    GetShowfile,
    GetShowfiles,
)
from ..services.shows import ShowService

show_router = APIRouter(tags=["show"])

logger = logging.getLogger("AAAAAA")


@show_router.post("/api/shows")
async def post_create_show(
    create_show: CreateShow,
    db=Depends(get_db),
    current_user=Depends(require_programmer),
):
    logger.warning(current_user)
    show_service = ShowService(db)
    new_show = await show_service.create_showfile(create_show, current_user)
    return new_show


@show_router.get("/api/shows")
async def get_shows(
    page: int = 1,
    limit: int = 100,
    current_user=Depends(require_operator),
    db=Depends(get_db),
):
    service = ShowService(db)
    showfiles = await service.get_showfiles(
        GetShowfiles(page=page, limit=limit, user=str(current_user.id))
    )
    return showfiles


@show_router.get("/api/show/{show_id}/patch")
async def get_patching(
    show_id: str, db=Depends(get_db), current_user=Depends(require_operator)
):
    service = ShowService(db)
    patch = await service.get_patching(
        GetShowfile(user=str(current_user.id), id=str(show_id))
    )
    return patch


@show_router.post("/api/shows/{show_id}/scenes")
async def post_create_scene(
    show_id: str,
    scene_definition: CreateScene,
    db=Depends(get_db),
    current_user=Depends(require_programmer),
):
    service = ShowService(db)
    scene = await service.create_scene(scene_definition)
    return scene


@show_router.put("/api/shows/scenes/{scene_id}/fixture-definition")
async def put_create_fixture_definition(
    scene_id: str,
    fixture_definition: CreateFixturesInSceneRequest,
    db=Depends(get_db),
    current_user=Depends(require_programmer),
):
    try:
        fixture_def = CreateFixturesInScene(
            scene_id=scene_id,
            fixture_id=fixture_definition.fixture_id,
            attribute=fixture_definition.attribute,
            value=fixture_definition.value,
        )

        service = ShowService(db)
        fix_def = await service.add_fixtures_to_scene(fixture_def)
    except DuplicateEntryError as e:
        raise HTTPException(409, detail=str(e))
    except Exception:
        raise HTTPException(500)
    return fix_def

@show_router.delete("/api/show/{show_id}")
async def delete_show(show_id:str, current_user = Depends(require_programmer), db = Depends(get_db)):
    show_service = ShowService(db)
    await show_service.delete_show(show_id)
    