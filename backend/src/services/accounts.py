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

import re
from datetime import datetime, timedelta, timezone
from jwt import encode, decode
from pwdlib import PasswordHash
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..core import settings
from ..core.exc import DuplicateEntryError, InvalidPasswordError, Unauthorised
from ..models.accounts import Accounts, UsedRefreshToken, Role
from ..schemas.accounts import UserCreate, UserGet, UserLogin
import uuid
import asyncio

# Password policy: 8-64 chars, at least one uppercase, one lowercase, one digit, and one special char.
PATTERN = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,64}$'
)


class AccountService:
    """
    Service layer for managing user accounts, handling secure password hashing
    via pwdlib and JWT-based authorisation.
    """

    _refresh_counter = 0
    _counter_lock = asyncio.Lock()
    password_hash_helper = PasswordHash.recommended()

    def __init__(self, session: AsyncSession):
        """
        Initialise the AccountService with a database session.

        :param session: The asynchronous database session.
        :type session: AsyncSession
        """
        self.db = session

    async def get_user(self, user: UserGet):
        """
        Retrieve a user instance based on ID or username.

        :param user: The criteria to search for the user.
        :type user: UserGet
        :raises ValueError: If neither ID nor username is provided.
        :return: The account instance or None if not found.
        :rtype: Accounts | None
        """
        if user.id:
            qry = select(Accounts).where(Accounts.id == user.id)
        elif user.username:
            qry = select(Accounts).where(Accounts.username == user.username.lower())
        else:
            raise ValueError("Either id or username must be specified")

        result = await self.db.execute(qry)
        return result.scalar_one_or_none()

    async def create_user(
        self, user: UserCreate, role_name: str = "viewer"
    ) -> Accounts:
        """
        Create a new user with a pre-defined role.

        :param user: The user data from the schema.
        :param role_name: The string name of the role (e.g., 'admin').
        """
        # 1. Get the role ID first
        role_qry = select(Role).where(Role.name == role_name)
        role_res = await self.db.execute(role_qry)
        role_obj = role_res.scalar_one_or_none()

        if not role_obj:
            raise ValueError(f"Role '{role_name}' not found in database.")

        # 2. Create account with the role_id
        account = Accounts(
            username=user.username.lower(),
            password=self.password_hash(user.password),
            first_name=user.first_name,
            last_name=user.last_name,
            role_id=role_obj.id,  # Use the UUID from the role we just found
            is_active=True,
        )

        self.db.add(account)
        try:
            await self.db.commit()
            await self.db.refresh(account)
            return account
        except IntegrityError:
            await self.db.rollback()
            raise DuplicateEntryError("User already exists")

    async def add_role(self, user: UserGet, role_name: str) -> Accounts:
        """
        Assign a specific role to a user.

        :param user: The criteria to search for the user (ID or username).
        :type user: UserGet
        :param role_name: The name of the role to assign.
        :type role_name: str
        :raises ValueError: If the role or the user is not found.
        :return: The updated account instance.
        :rtype: Accounts
        """
        # 1. Fetch the role instance correctly
        role_qry = select(Role).where(Role.name == role_name)
        role_result = await self.db.execute(role_qry)
        role = role_result.scalar_one_or_none()

        if not role:
            raise ValueError(f"Role '{role_name}' not found.")

        # 2. Fetch the user account
        # Note: Ensure your get_user method doesn't raise scalar_one() errors
        # if the user is missing; using scalar_one_or_none inside get_user is safer.
        account = await self.get_user(user)
        if not account:
            raise ValueError("User not found.")

        # 3. Check if the user already has the role to avoid duplicates
        if role != account.role:
            account.role = role_result

            try:
                await self.db.commit()
                # Refresh to ensure the relationship state is updated
                await self.db.refresh(account)
            except Exception:
                await self.db.rollback()
                raise

        return account

    async def authorise_user(self, user: UserLogin):
        """
        Verify credentials and return a JWT. Updates the hash if security
        parameters are outdated.

        :param user: The login credentials.
        :type user: UserLogin
        :raises Unauthorised: If verification fails.
        :return: An encoded JWT string.
        :rtype: str
        """
        qry = (
            select(Accounts)
            .where(Accounts.username == user.username.lower())
            .where(Accounts.is_active == True)
        )

        res = await self.db.execute(qry)
        account = res.scalar_one_or_none()

        if not account:
            raise Unauthorised("Username or Password is incorrect.")

        # verify_and_update returns a result object (verified: bool, updated_hash: str | None)
        verified, updated_hash = self.password_hash_helper.verify_and_update(
            user.password, account.password
        )

        if not verified:
            raise Unauthorised("Username or Password is incorrect.")

        # If a re-hash is recommended by pwdlib, we update it in the database.
        if updated_hash:
            update_qry = (
                update(Accounts)
                .where(Accounts.id == account.id)
                .values(password=updated_hash)
            )
            await self.db.execute(update_qry)
            await self.db.commit()

        return self.encode_jwt(sub=account.id)

    def password_hash(self, password) -> str:
        """
        Validate a password against the policy and return a secure hash.

        :param password: The plain-text password.
        :type password: str
        :raises InvalidPasswordError: If the password policy is not met.
        :return: The secure password hash.
        :rtype: str
        """
        if PATTERN.match(password):
            return self.password_hash_helper.hash(password)
        raise InvalidPasswordError("Password did not meet password policy.")

    async def refresh_session(self, refresh_token: str):
        """
        Validate a refresh token and issue a new set of tokens.

        :param refresh_token: The encoded JWT refresh token.
        :type refresh_token: str
        :raises Unauthorised: If the token is invalid or the session has expired.
        :return: New access and refresh tokens with their expiry dates.
        :rtype: tuple
        """
        try:
            payload = self.decode_jwt(refresh_token)

            # Security check: Ensure this is a refresh token
            if payload.get("scope") != "refresh":
                raise Unauthorised("Invalid token scope.")
            qry = select(UsedRefreshToken).where(
                UsedRefreshToken.jti == uuid.UUID(payload.get("jti"))
            )
            res = await self.db.execute(qry)
            if res.scalar_one_or_none():
                raise Unauthorised("Access denied. Token reuse.")
            user_id = payload.get("sub")
            if not user_id:
                raise Unauthorised("Invalid token payload.")

            # Optional: Check database if user is still active
            user = await self.get_user(UserGet(id=user_id))
            if not user:
                raise Unauthorised("User not found.")

            # Return new tokens (this implements Token Rotation)
            used_token = UsedRefreshToken(
                jti=uuid.UUID(payload.get("jti")),
                user_id=uuid.UUID(payload.get("sub")),
                expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            )
            self.db.add(used_token)
            await self.db.commit()
            return self.encode_jwt(sub=user.id)
        except Exception as e:
            print(e)
            raise Unauthorised("Invalid or expired refresh token.")

    async def delete_refresh_tokens(self):
        now = datetime.now(tz=timezone.utc)
        qry = delete(UsedRefreshToken).where(UsedRefreshToken.expires_at < now)
        await self.db.execute(qry)
        await self.db.commit()

    @staticmethod
    def encode_jwt(sub):
        """
        Generate a JWT for the given subject with specific scopes.

        :param sub: The subject of the token (user ID).
        :type sub: str | int
        :return: A pair of (access_token, refresh_token) tuples.
        :rtype: tuple
        """
        now = datetime.now(tz=timezone.utc)

        # Base shared data
        base_payload = {
            "iss": "hyperion_backend",
            "iat": now,
            "nbf": now - timedelta(seconds=3),
            "sub": str(sub),
        }

        # Access Token Payload
        access_payload = base_payload.copy()
        access_payload.update(
            {
                "exp": now + timedelta(minutes=15, seconds=3),
                "jti": str(uuid.uuid7()),
                "scope": "access",  # Added to distinguish from refresh tokens
            }
        )

        # Refresh Token Payload
        refresh_payload = base_payload.copy()
        refresh_payload.update(
            {
                "exp": now + timedelta(days=7, seconds=3),
                "jti": str(uuid.uuid7()),
                "scope": "refresh",  # Crucial for the refresh_session check
            }
        )

        return (
            (
                encode(access_payload, key=settings.JWT_SECRET, algorithm="HS512"),
                access_payload["exp"],
            ),
            (
                encode(refresh_payload, key=settings.JWT_SECRET, algorithm="HS512"),
                refresh_payload["exp"],
            ),
        )

    @staticmethod
    def decode_jwt(token):
        print("damn", token)
        return decode(
            token, settings.JWT_SECRET, algorithms=["HS512"], issuer="hyperion_backend"
        )
