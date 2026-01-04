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
import logging
import asyncio

import redis.asyncio as redis
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
    Query
)

from ..core.database import get_db
from ..core.dependencies import get_current_device
from ..core.exc import Conflict, Unauthorised
from ..core.redis_db import get_redis
from ..core.security.access import require_admin, RoleChecker, ACL_VIEWER, require_viewer
from ..schemas.device_management import AuthenticateOTP
from ..schemas.dmx_processor import DMXFrameRequest
from ..services.device_management import DeviceService
from ..services.dmx_processor import DMXProcessor
from ..services.dmx_protocol import DMXProtocol
from ..engine.dmx_router import router
dmx_router = APIRouter(tags=["hyperion-dmx"])


logger = logging.getLogger("dmx")


@dmx_router.get("/api/dmx/otp-challenge")
async def get_otp_challenge(user=Depends(require_admin), db=Depends(get_db)):
    dev_mgmt = DeviceService(db)
    otp = await dev_mgmt.generate_unique_otp()
    return otp


@dmx_router.post("/api/dmx/otp-authenticate")
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


@dmx_router.post("/api/dmx/broadcast")
async def trigger_dmx(value: str, redis_client: redis.Redis = Depends(get_redis)):
    """
    Publishes a value to Redis. All connected WebSockets will receive this.
    """
    await redis_client.publish("hyperion:dmx:global", value)
    return {"status": "broadcast_sent", "value": value}


@dmx_router.post("/api/dmx/send-frame")
async def send_dmx_frame(
    frame: DMXFrameRequest, redis_client: redis.Redis = Depends(get_redis)
):
    """
    Takes a JSON DMX frame, packs it into binary, encodes to Base64,
    and broadcasts it via Redis.
    """
    transport_payload = DMXProtocol.to_transport(frame.universe, frame.values)

    await redis_client.publish("hyperion:dmx:global", transport_payload)

    return {"status": "sent", "bytes_size": len(frame.values) + 2}


@dmx_router.get("/api/dmx/commands")
async def send_dmx_commands(current_user =Depends(require_viewer)):
    return router.commands

@dmx_router.websocket("/dmx")
async def ws_show(
    websocket: WebSocket,
    device=Depends(get_current_device),
    redis_client: redis.Redis = Depends(get_redis),
):
    """
    WebSocket Endpoint for DMX Nodes using Redis Pub/Sub.
    """
    await websocket.accept()

    dmxp = DMXProcessor(websocket, redis_client)

    redis_task = asyncio.create_task(dmxp.subscribe_and_stream())

    try:
        while True:
            j = await websocket.receive_json()
            await dmxp.json_data(data=j)

    except WebSocketDisconnect:
        logger.info(f"Node {device.name} disconnected")
    except Exception as e:
        logger.error(str(e))
    finally:
        redis_task.cancel()


@dmx_router.websocket("/ws/engine")
async def ws_engine(
    websocket: WebSocket, redis_client: redis.Redis = Depends(get_redis), token = Query(...), db = Depends(get_db)
):
    """
    Handle real-time DMX engine updates via WebSocket and broadcast via Redis.

    This endpoint receives JSON frames from the frontend, transforms them
    into a packed binary format using the DMXProtocol, and publishes
    the result to the global Redis channel for all connected nodes.

    :param websocket: The active WebSocket connection from the frontend.
    :param redis_client: Redis instance used for Pub/Sub broadcasting.
    """
    await websocket.accept()
    logger.info("🚀 Frontend Engine connected to /ws/engine")

    checker = RoleChecker(ACL_VIEWER)
    user = await checker.verify_token(token=token, db=db)
    print(user)
    try:
        
        while True:
            data = await websocket.receive_json()
            data = dict(data)
            await router.dispatch(websocket, data, user, redis_client, db )
    except WebSocketDisconnect:
        logger.info("🔌 Frontend Engine disconnected")
    except Exception as e:
        logger.error(f"🔥 Critical error in ws_engine: {e}")
