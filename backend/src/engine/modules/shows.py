from ..dmx_router import router
from ...core.security.access import ACL_PROGRAMMER
from ...schemas.dmx_modules.shows import ShowRequest, CreateShow, ShowDeleteRequest
from ...services.shows import ShowService
import logging 

logger = logging.getLogger("hyperion.engine.show")
@router.command("shows.create", acl=ACL_PROGRAMMER, model=ShowRequest)
async def ws_create_show(ws, user, data, db):
    """Creates a show using the frontend websocket.
    
    :param ws: Active websocket connection.
    :param user: User from the frontend.

    """
    show_service = ShowService(db)
    show = await show_service.create_showfile(data.data, user)
    await ws.send_text(f"Showfile '{show.name}' created")
    

@router.command("shows.delete", acl=ACL_PROGRAMMER, model=ShowDeleteRequest)
async def ws_delete_show(ws, data, db):
    """Creates a show using the frontend websocket.
    
    :param ws: Active websocket connection.
    :param user: User from the frontend.

    """
    show_service = ShowService(db)
    x = data.data.show_id
    print("loool",x)
    if x.startswith("show_id='"):
        x = x.replace("show_id='", "").replace("'", "")
    print(x)    
    await show_service.delete_show(x)
    await ws.send_text(f"Showfile deleted.")

