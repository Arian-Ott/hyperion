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

import uuid

from sqlalchemy import desc, select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.dmx.scenes import Scene, SceneFixtureValue
from ..models.fixtures import Fixture
from ..models.shows import Show
from ..schemas.show import (
    CreateFixturesInScene,
    CreateScene,
    CreateShow,
    GetShowfile,
    GetShowfiles,
)
from ..core.exc import DuplicateEntryError


class ShowService:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def create_showfile(self, create_show: CreateShow, user):
        print(create_show)
        show = Show(name=create_show.name, created_by=user.id)
        try:
            self.db.add(show)
            await self.db.commit()
            await self.db.refresh(show)
            return show
        except IntegrityError:
            await self.db.rollback()

    async def get_showfiles(self, get_showfiles: GetShowfiles):
        """
        Fetch show files using either offset-based or keyset pagination.

        :param get_showfiles: DTO containing page, limit, and optionally last_id.
        :return: A sequence of Show objects.
        """
        effective_limit = min(get_showfiles.limit, 512)

        qry = select(Show).order_by(desc(Show.id)).limit(effective_limit + 1)

        calculated_offset = (get_showfiles.page - 1) * effective_limit
        qry = qry.offset(calculated_offset)

        result = await self.db.execute(qry)
        showfiles = result.scalars().all()

        return showfiles

    async def get_patching(self, showfile: GetShowfile):
        qry = (
            select(Fixture)
            .join(Show, Fixture.show_id == Show.id)
            .where(
                Fixture.show_id == uuid.UUID(showfile.id),
                Show.created_by == uuid.UUID(showfile.user),
            )
            .order_by(desc(Fixture.id))
        )
        result = await self.db.execute(qry)
        return result.scalars().all()

    async def create_scene(self, scene_definition: CreateScene):
        scene = Scene(
            show_id=uuid.UUID(scene_definition.show_id, version=7),
            sid=scene_definition.sid,
            name=scene_definition.name,
        )
        try:
            self.db.add(scene)
            await self.db.commit()
            await self.db.refresh(scene)
        except IntegrityError:
            await self.db.rollback()
        return scene

    async def add_fixtures_to_scene(self, fixture_definition: CreateFixturesInScene):
        fix_def = SceneFixtureValue(
            scene_id=uuid.UUID(fixture_definition.scene_id),
            fixture_id=uuid.UUID(fixture_definition.fixture_id),
            attribute=fixture_definition.attribute,
            value=fixture_definition.value,
        )
        try:
            self.db.add(fix_def)
            await self.db.commit()
            await self.db.refresh(fix_def)
        except IntegrityError:
            await self.db.rollback()
            raise DuplicateEntryError("Duplicate fixture definition found.")
        return fix_def

    async def create_cue(self):
        raise NotImplementedError
    
    async def delete_show(self, show_id):
        try:
            qry = delete(Show).where(Show.id == uuid.UUID(show_id))
            await self.db.execute(qry)
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()