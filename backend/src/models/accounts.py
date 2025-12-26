import uuid
from sqlalchemy import Column, String, ForeignKey, Table, Boolean, DateTime
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
    role_id = Column(UUID, ForeignKey(
        "roles.id", ondelete="RESTRICT"), nullable=False)
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
