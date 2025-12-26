from fastapi import APIRouter, WebSocket, Depends, HTTPException
from fastapi import status
from ..core.database import get_db
from ..core.security.access import require_admin
import secrets
import string
from ..services.device_management import DeviceService
from ..schemas.device_management import AuthenticateOTP
from ..core.exc import Conflict, Unauthorised

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
async def ws_show(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_bytes()
        print(data)
        return data
