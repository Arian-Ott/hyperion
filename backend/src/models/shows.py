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
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Table,
    Boolean,
    DateTime,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship

from ..core.database import Base, TimestampMixin


class Show(Base, TimestampMixin):
    """
    Represents a lighting show file.

    :param id: User-friendly integer identifier
    :param name: Unique name of the show
    :param created_by: Reference to the account that created the show
    :param description: Optional details about the production
    """

    __tablename__ = "shows"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), unique=True, nullable=False)
    created_by = Column(ForeignKey("accounts.id"), nullable=False)
    description = Column(String, nullable=True)

    fixtures = relationship(
        "Fixture", back_populates="show", cascade="all, delete-orphan"
    )


class Manufacturer(Base):
    """
    Represents a hardware manufacturer.

    :param short_name: Abbreviated name (e.g. 'MA', 'GLP')
    :param name: Full legal name (e.g. 'MA Lighting')
    """

    __tablename__ = "manufacturer"
    id = Column(Integer, autoincrement=True, primary_key=True)
    short_name = Column(String(16), unique=True, nullable=False)
    name = Column(String(128), nullable=False)

    fixture_types = relationship("FixtureType", back_populates="manufacturer")


class FixtureCategory(Base):
    """
    Represents a category of lighting equipment.

    :param name: Category name (e.g. 'Moving Light', 'LED Wash', 'Dimmer')
    """

    __tablename__ = "fixture_categories"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)

    fixture_types = relationship("FixtureType", back_populates="category")


class FixtureType(Base):
    """
    The technical blueprint/profile for a fixture model.

    :param model_name: Name of the product (e.g. 'Pointe')
    :param mode: The DMX mode description (e.g. 'Mode 1 24Ch')
    :param channel_count: Total number of DMX channels used
    """

    __tablename__ = "fixture_types"
    id = Column(Integer, autoincrement=True, primary_key=True)
    model_name = Column(String(128), nullable=False)
    mode = Column(String(64), nullable=False)
    channel_count = Column(Integer, nullable=False)

    manufacturer_id = Column(ForeignKey("manufacturer.id"), nullable=False)
    category_id = Column(ForeignKey("fixture_categories.id"), nullable=False)

    manufacturer = relationship("Manufacturer", back_populates="fixture_types")
    category = relationship("FixtureCategory", back_populates="fixture_types")
    instances = relationship("Fixture", back_populates="fixture_type")


class Fixture(Base):
    """
    The actual patched instance within a show.

    :param fid: User Number / Fixture ID for console selection
    :param name: Custom name for the unit
    :param universe: Target DMX universe
    :param dmx_address: Starting DMX address
    """

    __tablename__ = "fixtures"
    id = Column(Integer, autoincrement=True, primary_key=True)
    fid = Column(Integer, nullable=False)
    name = Column(String(128), nullable=True)
    universe = Column(Integer, default=1, nullable=False)
    dmx_address = Column(Integer, nullable=False)

    show_id = Column(ForeignKey("shows.id"), nullable=False)
    fixture_type_id = Column(ForeignKey("fixture_types.id"), nullable=False)

    show = relationship("Show", back_populates="fixtures")
    fixture_type = relationship("FixtureType", back_populates="instances")
