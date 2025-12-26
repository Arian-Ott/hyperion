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

import orjson
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import AsyncGenerator
from sqlalchemy.schema import MetaData
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.schema import MetaData
from . import settings

engine = create_async_engine(
    settings.db_url,
    echo=False,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    query_cache_size=1200,  # Cache für SQL-Kompilierung vergrössern
    json_serializer=lambda obj: orjson.dumps(obj).decode(),
    json_deserializer=orjson.loads,
)


async_session_factory = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession, autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an optimised asynchronous database session.

    The session is managed via a context manager to ensure that resources
    are released and transactions are rolled back in case of failure.
    Autoflush is disabled by default to reduce unnecessary database roundtrips.

    :yield: An instance of AsyncSession for database operations.
    :rtype: AsyncGenerator[AsyncSession, None]
    """
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models using declarative mapping.

    This class provides a shared metadata object with a naming convention
    for constraints and default table arguments optimised for MariaDB.
    """

    metadata = MetaData(naming_convention=naming_convention)

    # Global table arguments for MariaDB performance and compatibility
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }


class TimestampMixin:
    """
    A mixin to provide automatic timestamps for models.

    :ivar created_at: The date and time when the record was first created.
    :ivar updated_at: The date and time when the record was last modified.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        sort_order=999,  # Ensures it's usually at the end of the table
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        sort_order=1000,
    )


async def init_db() -> None:
    """
    Initialise the database tables.

    This function uses the asynchronous engine to run the synchronous
    metadata creation process. It should typically be called during
    the application startup phase.

    :return: None
    """
    async with engine.begin() as conn:
        if settings.DROP_DB and settings.DEBUG:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
