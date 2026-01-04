from ..dmx_router import router
from ...core.security.access import ACL_PROGRAMMER
from ...schemas.dmx_modules.shows import ShowRequest, CreateShow
from ...services.shows import ShowService
import logging 

logger = logging.getLogger("enfgggg")
@router.command("shows.create", acl=ACL_PROGRAMMER, model=ShowRequest)
async def ws_create_show(ws, user, data, db):
    """Creates a show using the frontend websocket.
    
    :param ws: Active websocket connection.
    :param user: User from the frontend.
    :para
    """
    print(data)
    show_service = ShowService(db)
    logger.info(data)
    show = await show_service.create_showfile(data.data, user)
    
    await ws.send_text(str(show.name))