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
from uuid import UUID
from typing import Optional, Self

from pydantic import BaseModel, Field, field_validator, model_validator
from faker import Faker
from datetime import datetime

# Initialise Faker with British English locale as per your preference
fake = Faker(locale=["en_GB"])

# Regular expression for password strength
PASSWORD_REGEX = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,64}$'


class UserGet(BaseModel):
    """
    Schema for retrieving user information.
    """

    id: Optional[UUID] = None
    username: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    username: str
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    """
    Data transfer object for user registration.

    This model enforces a strict password policy and ensures password
    confirmation matches. It also provides examples and descriptions
    for Swagger documentation.
    """

    username: str = Field(
        ...,
        examples=[fake.user_name()],
        description="A unique username for the new account.",
    )
    first_name: str = Field(
        ..., min_length=1, max_length=128, examples=[fake.first_name()]
    )
    last_name: str = Field(
        ..., min_length=1, max_length=128, examples=[fake.last_name()]
    )
    password: str = Field(
        ...,
        description="Must include upper, lower, digit, and special character.",
        examples=["Test1234!"],
    )
    password_confirm: str = Field(
        ..., description="Must match the password.", examples=["Test1234!"]
    )


class UserLogin(BaseModel):
    username: str
    password: str
