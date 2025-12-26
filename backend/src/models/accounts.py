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
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Table,
    Boolean,
    DateTime,
    Integer,
    Index,
)
from sqlalchemy import UUID
from datetime import datetime

from sqlalchemy.orm import relationship
from ..core.database import Base, TimestampMixin


class Role(Base):
    """
    Represent a security role assigned to accounts.

    This model handles the simplest form of RBAC where access is determined
    solely by the role name.

    :param name: The unique name of the role (e.g. 'administrator', 'manager').
    """

    __tablename__ = "roles"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(64), unique=True, nullable=False)
    system_role = Column(Boolean, default=False, nullable=False)
    accounts = relationship("Accounts", back_populates="role")


class Accounts(Base, TimestampMixin):
    """
    Represent an individual user account with multiple possible roles.

    :param username: The unique identifier for the user.
    :param roles: A collection of Role objects assigned to this account.
    """

    __tablename__ = "accounts"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    username = Column(String(64), unique=True, index=True, nullable=False)
    password = Column(String(256), nullable=False)
    first_name = Column(String(128), nullable=False)
    last_name = Column(String(128), nullable=False)
    role_id = Column(UUID, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    is_active = Column(Boolean, default=True)
    role = relationship("Role", back_populates="accounts", lazy="joined")


class UsedRefreshToken(Base):
    """
    Model to track used refresh tokens to prevent replay attacks.
    """

    __tablename__ = "used_refresh_tokens"

    jti = Column(UUID, primary_key=True, index=True)
    user_id = Column(ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime, nullable=False)


class HyperionClients(Base, TimestampMixin):
    """
    Represent a client entity. This table stores persistent identity data.

    :param id: The unique identifier for the client.
    :param name: The unique name of the client.
    :param is_active: Whether the client account is enabled.
    :param token: The single associated session token (1:1 relationship).
    """

    __tablename__ = "clients"

    id = Column(UUID, default=uuid.uuid7, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    is_active = Column(Boolean, default=True, nullable=False)

    token = relationship(
        "ClientTokens",
        back_populates="client_obj",
        uselist=False,
        cascade="all, delete-orphan",
    )


class ClientTokens(Base):
    """
    Store the current active session token for a client.

    :param id: Unique identifier for the token record.
    :param client_id: Foreign key linking to the owner client.
    :param token_hash: SHA3-512 hash of the active token.
    :param expires_at: Expiry timestamp for the session.
    :param client_obj: Reference back to the HyperionClients instance.
    """

    __tablename__ = "client_tokens"

    id = Column(UUID, default=uuid.uuid7, primary_key=True)
    client_id = Column(ForeignKey("clients.id"), unique=True, nullable=False)

    token_hash = Column(String(128), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    client_obj = relationship("HyperionClients", back_populates="token")


class OTPModel(Base, TimestampMixin):
    __tablename__ = "otp_challenges"
    id = Column(Integer, primary_key=True, autoincrement=True)
    otp = Column(String(128), unique=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    __table_args__ = (Index("ix_otp_hash", "otp"),)
