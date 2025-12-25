from ..schemas.accounts import UserGet, UserCreate
from ..models.accounts import Accounts
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from ..core.exc import InvalidPasswordError, DuplicateEntryError
from sqlalchemy.exc import IntegrityError
import re


PATTERN = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,64}$'
)


class AccountService:
    pw_context = CryptContext(schemes=["argon2"])

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_user(self, user: UserGet):
        if user.id:
            qry = select(Accounts).where(Accounts.id == user.id)
        elif user.username:
            qry = select(Accounts).where(Accounts.username == user.username.lower())
        else:
            raise ValueError("Either id or username must be specified")
        result = await self.db.execute(qry)
        return result.scalar_one_or_none()

    async def create_user(self, user: UserCreate):
        if not user.password == user.password_confirm:
            raise InvalidPasswordError("Password and password_confirm did not match.")
        account = Accounts(
            username=user.username.lower(),
            password=self.password_hash(user.password),
            first_name=user.first_name,
            last_name=user.last_name,
        )
        try:
            self.db.add(account)
            await self.db.commit()
            await self.db.refresh(account)
        except IntegrityError:
            await self.db.rollback()
            raise DuplicateEntryError("User already exists")
        return account

    def password_hash(self, password):
        if PATTERN.match(password):
            return AccountService.pw_context.hash(password)
        raise InvalidPasswordError("Password did not meet password policy.")
