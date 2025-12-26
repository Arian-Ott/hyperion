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
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, delete
import hashlib
import secrets
import string
import logging
from datetime import datetime, timezone, timedelta

from ..models.accounts import OTPModel, HyperionClients, ClientTokens
from ..schemas.device_management import GetOTP, AuthenticateOTP, AuthenticatedDevice
from ..core.exc import Unauthorised, Conflict

logger = logging.getLogger("device_service")


class DeviceService:
    """
    Service responsible for managing device-related operations such as OTP generation
    and authentication.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialise the DeviceService with a database session.

        :param session: The asynchronous database session.
        :type session: AsyncSession
        """
        self.db = session

    async def generate_unique_otp(self) -> GetOTP:
        """
        Generate a unique 6-character alphanumeric OTP and persist its hash.

        The function attempts to save a SHA3-512 hash of the PIN to the database.
        If a collision occurs (IntegrityError), it retries up to 5 times.
        PINs are valid for 15 minutes.

        :raises RuntimeError: If a unique PIN cannot be generated within the retry limit.
        :return: A schema containing the plain PIN and its expiry timestamp.
        :rtype: GetOTP
        """
        max_retries = 5
        alphabet = string.digits + string.ascii_uppercase

        validity_period = timedelta(minutes=15)

        for retry in range(1, max_retries + 1):
            try:
                pairing_pin = "".join(secrets.choice(alphabet) for _ in range(6))
                expiry_time = datetime.now(tz=timezone.utc) + validity_period

                pairing_hash = hashlib.sha3_512(pairing_pin.encode()).hexdigest()

                otp_entry = OTPModel(otp=pairing_hash, expires_at=expiry_time)

                self.db.add(otp_entry)
                await self.db.commit()

                return GetOTP(otp=pairing_pin, exp=expiry_time)

            except IntegrityError:
                await self.db.rollback()
                logger.warning(
                    "OTP collision detected on attempt %s of %s. Retrying...",
                    retry,
                    max_retries,
                )

        logger.critical(
            "Failed to generate a unique OTP after %s attempts.", max_retries
        )
        raise RuntimeError(
            f"Could not generate a unique pairing PIN after {max_retries} attempts."
        )

    async def authenticate_otp(self, auth_otp: AuthenticateOTP):
        """
        Authenticate a device using an OTP and issue a long-lived access token.

        This method verifies the OTP, checks its expiry, ensures atomicity when
        creating client records, and invalidates the OTP upon success.

        :param auth_otp: The schema containing the OTP and device name.
        :type auth_otp: AuthenticateOTP
        :raises Unauthorised: If the OTP is invalid or expired.
        :raises IntegrityError: If the client name already exists.
        :return: The plain-text access token for the client.
        :rtype: str
        """
        otp_hash = hashlib.sha3_512(auth_otp.otp.encode()).hexdigest()

        qry = select(OTPModel).where(OTPModel.otp == otp_hash)
        result = await self.db.execute(qry)
        otp_record = result.scalar_one_or_none()

        if not otp_record:
            raise Unauthorised("Device registration failed. Invalid or expired OTP.")

        now = datetime.now(timezone.utc)
        otp_expiry = otp_record.expires_at
        if otp_expiry.tzinfo is None:
            otp_expiry = otp_expiry.replace(tzinfo=timezone.utc)
        if otp_expiry < now:
            await self.db.delete(otp_record)
            await self.db.commit()
            raise Unauthorised("Device registration failed. Invalid or expired OTP.")

        token_plain = secrets.token_hex(64)
        token_hash = hashlib.sha3_512(token_plain.encode()).hexdigest()
        exp = now + timedelta(days=30)

        try:
            client = HyperionClients(name=auth_otp.name)
            self.db.add(client)

            await self.db.flush()

            client_token = ClientTokens(
                client_id=client.id, token_hash=token_hash, expires_at=exp
            )
            self.db.add(client_token)

            await self.db.delete(otp_record)

            await self.db.commit()

            return AuthenticatedDevice(device_secret=token_plain, exp=exp)

        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Integrity error during device registration: {e}")
            raise Conflict("Device name already exists.")
