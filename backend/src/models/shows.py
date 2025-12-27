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
    UUID,
)
from sqlalchemy.orm import relationship

from ..core.database import Base, TimestampMixin


class Show(Base, TimestampMixin):
    """
    Container for a specific project or event.
    Allows multiple shows to exist in the same database.
    """

    __tablename__ = "shows"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid7)
    name = Column(String(100), nullable=False, unique=True)
    created_by = Column(ForeignKey("accounts.id"))

    fixtures = relationship(
        "Fixture", back_populates="show", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Show(name='{self.name}')>"


class ShowAccess(Base, TimestampMixin):
    __tablename__ = "show_access"
    show_id = Column(ForeignKey("shows.id"), primary_key=True)
    granted_to = Column(ForeignKey("accounts.id"), primary_key=True)
    granted_by = Column(ForeignKey("accounts.id"), primary_key=True)
