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

from fastapi import Request
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    APIKeyCookie,
)

from ..core.database import get_db
from ..services.accounts import AccountService
from ..schemas.accounts import UserCreate, UserResponse, UserLogin, UserGet
from ..core.exc import DuplicateEntryError, InvalidPasswordError, Unauthorised

account_router = APIRouter(prefix="/api", tags=["accounts"])

cookie_scheme = APIKeyCookie(name="access_token")


@account_router.post("/accounts", response_model=UserResponse)
async def post_create_account(account: UserCreate, session=Depends(get_db)):
    user_service = AccountService(session)
    try:
        user = await user_service.create_user(account, "viewer")

    except DuplicateEntryError as e:
        raise HTTPException(409, detail=str(e))
    except InvalidPasswordError as e:
        raise HTTPException(422, detail=str(e))
    except Exception:
        raise HTTPException(500)

    return user


@account_router.get("/accounts", response_model=UserResponse)
async def get_signin_account(session=Depends(get_db), token=Depends(cookie_scheme)):
    print(token)
    payload = AccountService.decode_jwt(token)

    user_service = AccountService(session)
    user = await user_service.get_user(UserGet(id=payload.get("sub")))
    if not user:
        raise HTTPException(404, detail="User not found.")

    return user


@account_router.post("/accounts/login")
async def post_login(
    form: OAuth2PasswordRequestForm = Depends(), session=Depends(get_db)
):
    """
    Authenticate a user using a JSON body and return a JWT.

    :param login_data: The credentials provided as JSON.
    :type login_data: UserLogin
    :param session: The asynchronous database session.
    :type session: AsyncSession
    :raises Unauthorised: If the credentials are invalid.
    :return: The access token and its type.
    :rtype: dict
    """
    user_service = AccountService(session)
    login_data = UserLogin(username=form.username, password=form.password)
    try:
        access_token, refresh_token = await user_service.authorise_user(login_data)
        print(access_token[0])
        response = JSONResponse(
            {"access_token": access_token[0], "token_type": "bearer"}
        )
        response.set_cookie(
            "refresh_token",
            value=refresh_token[0],
            httponly=True,
            expires=refresh_token[1],
            secure=True,
            samesite="lax",
        )
        response.set_cookie(
            "access_token",
            value=access_token[0],
            httponly=True,
            expires=access_token[1],
            secure=True,
            samesite="lax",
        )
        return response
    except Unauthorised as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(e)
        raise HTTPException(500)


@account_router.post("/accounts/refresh")
async def post_refresh_token(request: Request, session=Depends(get_db)):
    """
    Refresh the session tokens using the refresh_token cookie.

    :param request: The incoming request to access cookies.
    :type request: Request
    :param session: The database session.
    :type session: AsyncSession
    :return: A response updating the access and refresh cookies.
    :rtype: JSONResponse
    """
    # 1. Token aus dem Cookie extrahieren
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    user_service = AccountService(session)

    try:
        # 2. Service aufrufen, um neue Tokens zu generieren
        new_access, new_refresh = await user_service.refresh_session(refresh_token)

        response = JSONResponse(content={"detail": "Tokens refreshed"})

        # 3. Neue Cookies setzen (Token Rotation)
        response.set_cookie(
            "access_token",
            value=new_access[0],
            httponly=True,
            expires=new_access[1],
            secure=True,
            samesite="lax",
        )
        response.set_cookie(
            "refresh_token",
            value=new_refresh[0],
            httponly=True,
            expires=new_refresh[1],
            secure=True,
            samesite="lax",
        )

        return response

    except Unauthorised as e:
        raise HTTPException(status_code=401, detail=str(e))
