from fastapi import FastAPI
import uvicorn

from .core import settings
from .core.startup import startup
from .routers.accounts import account_router

app = FastAPI(title="Hyperion DMX", debug=settings.DEBUG)


app.include_router(account_router)
app.add_event_handler("startup", startup)

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG
    )
