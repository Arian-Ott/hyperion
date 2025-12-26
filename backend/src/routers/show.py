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

from fastapi import APIRouter, WebSocket, Depends, HTTPException
from fastapi import status
from ..core.database import get_db
from ..core.security.access import require_admin
import secrets
import string
from ..services.device_management import DeviceService
from ..schemas.device_management import AuthenticateOTP
from ..core.exc import Conflict, Unauthorised
from ..core.dependencies import get_current_device
from ..services.dmx_processor import DMXProcessor

show_router = APIRouter(tags=["hyperion-dmx"])


@show_router.get("/api/dmx/otp-challenge")
async def get_otp_challenge(user=Depends(require_admin), db=Depends(get_db)):
    dev_mgmt = DeviceService(db)
    otp = await dev_mgmt.generate_unique_otp()
    return otp


@show_router.post("/api/dmx/otp-authenticate")
async def post_authenticate_otp(auth_otp: AuthenticateOTP, db=Depends(get_db)):
    dev_mgmt = DeviceService(db)
    try:
        auth = await dev_mgmt.authenticate_otp(auth_otp)
    except Unauthorised as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Conflict as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return auth


@show_router.websocket("/dmx")
async def ws_show(websocket: WebSocket, device=Depends(get_current_device)):
    await websocket.accept()
    dmxp = DMXProcessor(websocket)
    while True:
        pass
            
