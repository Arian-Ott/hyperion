from ...models.accounts import Role, Accounts
from ...services.accounts import AccountService
from typing import List
from enum import Enum
from fastapi import Depends
from ...routers.accounts import cookie_scheme
from ..database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from uuid import UUID
from fastapi import HTTPException
class UserRole(str, Enum):
    ADMIN = "admin"
    TECHNICAL_LEAD = "technical_lead"
    PROGRAMMER = "programmer"
    OPERATOR = "operator"
    VIEWER = "viewer"
    SUSPENDED = "suspended"

class RoleChecker:
    
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = [role.value for role in allowed_roles]
        

    async def __call__(self, token: str = Depends(cookie_scheme), db: AsyncSession = Depends(get_db)):
        payload = AccountService.decode_jwt(token)

        qry = (
            select(Accounts)
            .options(joinedload(Accounts.role))
            .where(Accounts.id == UUID(payload["sub"]))
        )
        result = await db.execute(qry)
        user = result.unique().scalar_one_or_none()

        if not user:
            raise HTTPException(401, "User not found.")

        

        if not user.is_active:
            raise HTTPException(403, "Account is suspended.")
    
        if user.role.name not in self.allowed_roles:
            raise HTTPException(
                403, f"Required: {self.allowed_roles}, but you are: {user.role.name}")

        return user

ACL_ADMIN = [UserRole.ADMIN]
ACL_TECH_LEAD = [UserRole.ADMIN, UserRole.TECHNICAL_LEAD]
ACL_PROGRAMMER = [UserRole.ADMIN, UserRole.TECHNICAL_LEAD, UserRole.PROGRAMMER]
ACL_OPERATOR = [UserRole.ADMIN, UserRole.TECHNICAL_LEAD, UserRole.PROGRAMMER,UserRole.OPERATOR]
ACL_VIEWER = [UserRole.ADMIN, UserRole.TECHNICAL_LEAD, UserRole.PROGRAMMER, UserRole.OPERATOR, UserRole.VIEWER]

require_admin = RoleChecker(ACL_ADMIN)
require_tech_lead = RoleChecker(ACL_TECH_LEAD)
require_programmer = RoleChecker(ACL_PROGRAMMER)
require_operator = RoleChecker(ACL_OPERATOR)
require_viewer = RoleChecker(ACL_VIEWER)

