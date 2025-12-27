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
from ..core.database import get_db
from ..core.security.access import require_programmer
from ..schemas.show import CreateShow
from ..services.shows import ShowService
import logging

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
