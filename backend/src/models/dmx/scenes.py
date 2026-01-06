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

from sqlalchemy import UUID, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ...core.database import Base
from ..fixtures import AttributeType


class Scene(Base):
    """
    Represent a static lighting snapshot or 'look' within the system.

    A Scene serves as a data container for specific fixture intensities,
    colours, and positions. Unlike a :class:`Cue`, which manages timing
    and sequence logic, a Scene focuses strictly on the state of the
    lighting rig at a given moment.

    It organises fixture data through associations, allowing multiple
    cues to potentially reference the same visual state, thus promoting
    data reusability across a show.

    :param id: Unique identifier for the scene, utilising UUID v7.
    :type id: uuid.UUID
    :param sid: The Scene ID (Short ID), typically used for quick console
        commands or numerical sorting.
    :type sid: int
    :param name: An optional human-readable name for the visual look.
    :type name: str
    :param show_id: Foreign key linking the scene to its parent :class:`Show`.
    :type show_id: uuid.UUID
    :param show: The parent show object this scene belongs to.
    :type show: Show
    :param cues: A collection of :class:`Cue` objects that trigger this
        specific scene.
    :type cues: list[Cue]
    :param fixture_associations: A collection of specific fixture values
        (DMX data) that constitute this scene. Utilises 'selectin'
        loading for optimised database performance.
    :type fixture_associations: list[SceneFixtureValue]
    """

    __tablename__ = "scenes"
    id = Column(UUID, primary_key=True, default=uuid.uuid7)

    sid = Column(Integer, index=True, nullable=False)
    name = Column(String(32), nullable=True)
    show_id = Column(
        UUID, ForeignKey("shows.id", ondelete="CASCADE"), nullable=False
    )
    show = relationship("Show", back_populates="scenes")
    cues = relationship("Cue", back_populates="scene", cascade="all, delete-orphan")
    fixture_associations = relationship(
        "SceneFixtureValue",
        back_populates="scene",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class SceneFixtureValue(Base):
    """
    Represent the specific value of a fixture attribute within a scene.

    This model serves as the atom of the lighting control system, mapping
    a single physical or virtual attribute (such as Dimmer, Red, or Pan)
    to a concrete DMX value.

    A collection of these values constitutes a complete :class:`Scene`.
    By decoupling attributes from the fixture itself, the system allows
    for transparent control and granular updates to complex lighting rigs.

    :param id: Unique identifier for this attribute-value pair,
        utilising UUID v7.
    :type id: uuid.UUID
    :param scene_id: Reference to the :class:`Scene` that contains this value.
    :type scene_id: uuid.UUID
    :param fixture_id: Reference to the specific :class:`Fixture` being
        controlled.
    :type fixture_id: uuid.UUID
    :param attribute: The type of attribute being manipulated (e.g.,
        INTENSITY, TILT, CYAN).
    :type attribute: AttributeType
    :param value: The numerical DMX value, typically ranging from 0 to 255
        for 8-bit attributes.
    :type value: int
    :param scene: The parent scene relationship.
    :type scene: Scene
    :param fixture: The associated fixture object. Utilises 'joined'
        loading to ensure fixture metadata is available during DMX
        generation.
    :type fixture: Fixture
    """

    __tablename__ = "scene_fixture_values"

    id = Column(UUID, primary_key=True, default=uuid.uuid7)

    scene_id = Column(
        UUID,
        ForeignKey("scenes.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    fixture_id = Column(
        UUID,
        ForeignKey("fixtures.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    attribute = Column(Enum(AttributeType), nullable=False)

    value = Column(Integer, nullable=False)

    scene = relationship("Scene", back_populates="fixture_associations")

    fixture = relationship("Fixture", lazy="joined")
