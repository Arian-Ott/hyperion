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
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from ..models.fixtures import Manufacturer, FixtureType, FixtureChannel, Fixture
from ..schemas.fixtures import CreateFixtureType, CreateFixturePatch
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from ..models.fixtures import FixtureType, FixtureChannel
from ..schemas.fixtures import CreateFixtureType
import uuid


class FixtureService:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def create_fixture_type(self, fixture_type_data: CreateFixtureType):
        try:
            new_fixture_type = FixtureType(
                manufacturer_id=uuid.UUID(str(fixture_type_data.manufacturer_id)),
                mode_name=fixture_type_data.mode_name,
                model=fixture_type_data.model,
            )

            self.db.add(new_fixture_type)

            await self.db.flush()

            for channel in fixture_type_data.channels:
                new_channel = FixtureChannel(
                    fixture_type_id=new_fixture_type.id,
                    dmx_offset=channel.dmx_offset,
                    attribute=channel.attribute,
                    default_value=channel.default_value,
                    highlight_value=channel.highlight_value,
                    invert_default=channel.invert_default,
                )
                self.db.add(new_channel)

            await self.db.commit()

            await self.db.refresh(new_fixture_type)

            return new_fixture_type

        except IntegrityError:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            raise e  # Unbekannte Fehler auch hochwerfen

    async def patch_fixture(self, data: CreateFixturePatch):
        query = (
            select(FixtureType)
            .options(selectinload(FixtureType.channels))
            .where(FixtureType.id == data.fixture_type_id)
        )
        result = await self.db.execute(query)
        fixture_type = result.scalars().first()

        if not fixture_type:
            raise ValueError("Fixture Type not found")

        channel_count = len(fixture_type.channels)
        end_address = data.start_address + channel_count - 1

        # Check: Passt das überhaupt ins Universum?
        if end_address > 512:
            raise ValueError(
                f"Fixture fits not in Universe. Ends at {end_address} (>512)."
            )

        # 3. Kollisions-Check (Collision Detection)
        # Wir holen alle Geräte in DERSELBEN Show und IMSELBEN Universum
        existing_fixtures_query = (
            select(Fixture)
            .where(
                and_(Fixture.show_id == data.show_id, Fixture.universe == data.universe)
            )
            .options(
                selectinload(Fixture.fixture_type).selectinload(FixtureType.channels)
            )
        )

        existing_result = await self.db.execute(existing_fixtures_query)
        existing_fixtures = existing_result.scalars().all()

        # Jetzt prüfen wir mathematisch auf Überlappung
        for existing in existing_fixtures:
            # Größe des existierenden Geräts berechnen
            existing_len = len(existing.fixture_type.channels)
            existing_end = existing.start_address + existing_len - 1

            # Überlappungs-Formel: (StartA <= EndB) and (StartB <= EndA)
            if (data.start_address <= existing_end) and (
                existing.start_address <= end_address
            ):
                raise ValueError(
                    f"DMX Collision! Overlaps with '{existing.name}' (Addr: {existing.start_address}-{existing_end})"
                )

        # 4. Wenn alles okay ist -> Speichern
        new_fixture = Fixture(
            id=uuid.uuid7(),  # Falls du UUIDv7 manuell generierst, sonst weglassen
            show_id=data.show_id,
            fixture_type_id=data.fixture_type_id,
            name=data.name,
            fid=data.fid,
            universe=data.universe,
            start_address=data.start_address,
            invert_pan=data.invert_pan,
            invert_tilt=data.invert_tilt,
        )

        try:
            self.db.add(new_fixture)
            await self.db.commit()
            await self.db.refresh(new_fixture)
            return new_fixture
        except IntegrityError as e:
            await self.db.rollback()
            # Hier fängst du Unique Constraints ab (z.B. doppelte FID)
            raise ValueError("FID or Name already exists in this Show.")
