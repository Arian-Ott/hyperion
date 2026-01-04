from ..dmx_router import router 

from pydantic import BaseModel
from ...schemas.dmx_modules.status import PingRequest


@router.command("health.ping", model=PingRequest)
async def health(ws):
    await ws.send_text("Connection worked!")