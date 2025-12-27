# Hyperion
# Copyright (C) 2025 Arian Ott <arian.ott@ieee.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import enum
import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..core.database import Base


class AttributeType(str, enum.Enum):
    """
    Defines the possible types of DMX attributes.
    Used for type safety and mapping logic in the engine.

    :param DIMMER: Intensity control.
    :param STROBE: Flashing effects.
    :param SHUTTER: Physical or digital shutter.
    :param PAN: Horizontal movement.
    :param PAN_FINE: Fine horizontal movement.
    :param TILT: Vertical movement.
    :param TILT_FINE: Fine vertical movement.
    :param COLOR_RED: Red intensity.
    :param COLOR_GREEN: Green intensity.
    :param COLOR_BLUE: Blue intensity.
    :param COLOR_WHITE: White intensity.
    :param COLOR_WHEEL: Fixed colour wheel selection.
    :param FOG: Fog or smoke output.
    :param FAN: Cooling or effect fan speed.
    :param SPEED: General effect speed.
    :param UNKNOWN: Fallback for undefined attributes.
    """
    DIMMER = "dimmer"
    STROBE = "strobe"
    SHUTTER = "shutter"

    PAN = "pan"
    PAN_FINE = "pan_fine"
    TILT = "tilt"
    TILT_FINE = "tilt_fine"

    COLOR_RED = "color_red"
    COLOR_GREEN = "color_green"
    COLOR_BLUE = "color_blue"
    COLOR_WHITE = "color_white"
    COLOR_WHEEL = "color_wheel"

    FOG = "fog"
    FAN = "fan"
    SPEED = "speed"

    UNKNOWN = "unknown"


class Manufacturer(Base):
    """
    Represents a manufacturer of lighting fixtures.

    :param id: Unique identifier (UUIDv7).
    :param name: The commercial name of the manufacturer.
    :param website: Optional URL to the manufacturer's site.
    """
    __tablename__ = "manufacturers"

    id = Column(UUID(as_uuid=True), primary_key=True,
                index=True, default=uuid.uuid7)
    name = Column(String(100), nullable=False, unique=True)
    website = Column(String(200), nullable=True)

    # Relationships
    fixture_types = relationship("FixtureType", back_populates="manufacturer")

    def __repr__(self):
        return f"<Manufacturer(name='{self.name}')>"


class FixtureType(Base):
    """
    Defines the blueprint or profile of a specific fixture model.
    Links a manufacturer to specific DMX channels.

    :param id: Unique identifier (UUIDv7).
    :param manufacturer_id: Foreign key linking to the manufacturer.
    :param model: The model name of the fixture.
    :param mode_name: The specific DMX mode name.
    """
    __tablename__ = "fixture_types"

    id = Column(UUID(as_uuid=True), primary_key=True,
                index=True, default=uuid.uuid7)
    manufacturer_id = Column(UUID(as_uuid=True), ForeignKey(
        "manufacturers.id"), nullable=False)

    model = Column(String(100), nullable=False)
    mode_name = Column(String(50), default="Standard")

    # Relationships
    manufacturer = relationship(
        "Manufacturer", back_populates="fixture_types", lazy="joined")
    channels = relationship(
        "FixtureChannel",
        back_populates="fixture_type",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    instances = relationship("Fixture", back_populates="fixture_type")

    def __repr__(self):
        m_name = self.manufacturer.name if self.manufacturer else "Unknown"
        return f"<FixtureType(model='{self.model}', mode='{self.mode_name}', manufacturer='{m_name}')>"


class FixtureChannel(Base):
    """
    Maps a logical attribute to a DMX offset for a specific FixtureType.

    :param id: Internal database primary key.
    :param fixture_type_id: Foreign key linking to the fixture blueprint.
    :param dmx_offset: Relative address within the fixture.
    :param attribute: The type of DMX attribute.
    :param default_value: Standard DMX value.
    :param highlight_value: Value used for the highlight function.
    :param invert_default: Whether the default logic is inverted.
    """
    __tablename__ = "fixture_channels"

    id = Column(Integer, primary_key=True, index=True)
    fixture_type_id = Column(UUID(as_uuid=True), ForeignKey(
        "fixture_types.id"), nullable=False)

    dmx_offset = Column(Integer, nullable=False)
    attribute = Column(Enum(AttributeType), nullable=False)
    default_value = Column(Integer, default=0)
    highlight_value = Column(Integer, default=255)
    invert_default = Column(Boolean, default=False)

    # Relationships
    fixture_type = relationship("FixtureType", back_populates="channels")


class Fixture(Base):
    """
    Represents a concrete physical device patched in the DMX universe.

    :param id: Unique identifier (UUIDv7).
    :param name: Friendly name of the patched fixture.
    :param fixture_type_id: Foreign key linking to the blueprint.
    :param universe: The DMX universe index.
    :param start_address: The DMX start address.
    :param is_active: Toggle for whether the fixture is active.
    :param invert_pan: Inverts the pan movement.
    :param invert_tilt: Inverts the tilt movement.
    """
    __tablename__ = "fixtures"

    id = Column(UUID(as_uuid=True), primary_key=True,
                index=True, default=uuid.uuid7)
    name = Column(String(100), nullable=False, unique=True)
    fixture_type_id = Column(UUID(as_uuid=True), ForeignKey(
        "fixture_types.id"), nullable=False)

    universe = Column(Integer, default=0, nullable=False)
    start_address = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    invert_pan = Column(Boolean, default=False)
    invert_tilt = Column(Boolean, default=False)

    # Relationships
    fixture_type = relationship(
        "FixtureType", back_populates="instances", lazy="selectin")

    def __repr__(self):
        return f"<Fixture(name='{self.name}', address='{self.universe}.{self.start_address}')>"
