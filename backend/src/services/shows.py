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

from ..models.shows import Show
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from ..schemas.show import CreateShow, GrantShowfileAccess


class ShowService:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def create_showfile(self, create_show: CreateShow, user):
        show = Show(name=create_show.name, created_by=user.id)
        try:
            self.db.add(show)
            await self.db.commit()
            await self.db.refresh(show)
            return show
        except IntegrityError:
            await self.db.rollback()

    async def grant_showfile_access(self, showfile_access: GrantShowfileAccess):
        pass
