from fastapi import FastAPI
import uvicorn
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
from .core import settings
from .core.startup import startup
from .routers.accounts import account_router
from .routers.show import show_router

app = FastAPI(title="Hyperion DMX", debug=settings.DEBUG)


app.include_router(account_router)
app.add_event_handler("startup", startup)
app.include_router(show_router)
if __name__ == "__main__":
    uvicorn.run(
        "src.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG
    )
