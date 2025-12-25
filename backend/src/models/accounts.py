import uuid
from sqlalchemy import Column, String, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..core.database import Base, TimestampMixin


role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey(
        "roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", ForeignKey(
        "permissions.id", ondelete="CASCADE"), primary_key=True),
)


account_roles = Table(
    "account_roles",
    Base.metadata,
    Column("account_id", ForeignKey("accounts.id",
           ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey(
        "roles.id", ondelete="CASCADE"), primary_key=True),
)


class Permission(Base):
    """
    Represent an individual granular permission within the system.

    :param name: The unique identifier for the permission (e.g., 'user:write').
    :param description: A human-readable description of what this permission allows.
    """
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(64), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)


class Role(Base):
    """
    Represent a group of permissions assigned to users.

    :param name: The unique name of the role (e.g., 'administrator').
    :param permissions: A list of Permission objects associated with this role.
    """
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(64), unique=True, nullable=False)

    permissions = relationship(
        "Permission", secondary=role_permissions, backref="roles")


class Accounts(Base, TimestampMixin):
    """
    Represent a user account with assigned roles and credentials.

    :param username: Unique login name.
    :param roles: A list of Role objects assigned to this account.
    """
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True,
                index=True, default=uuid.uuid4)
    username = Column(String(64), unique=True, index=True, nullable=False)
    password = Column(String(256), nullable=False)
    first_name = Column(String(128), nullable=False)
    last_name = Column(String(128), nullable=False)

    roles = relationship("Role", secondary=account_roles, backref="accounts")
