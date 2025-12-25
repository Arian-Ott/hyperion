from fastapi import APIRouter, Depends, HTTPException
from ..core.database import get_db
from ..services.accounts import AccountService
from ..schemas.accounts import UserCreate, UserResponse
from ..core.exc import DuplicateEntryError, InvalidPasswordError

account_router = APIRouter(prefix="/api", tags=["accounts"])


@account_router.post("/accounts", response_model=UserResponse)
async def post_create_account(account: UserCreate, session=Depends(get_db)):
    user_service = AccountService(session)
    try:
        user = await user_service.create_user(account)
    except DuplicateEntryError as e:
        raise HTTPException(409, detail=str(e))
    except InvalidPasswordError as e:
        raise HTTPException(422, detail=str(e))
    except Exception:
        raise HTTPException(500)

    return user
