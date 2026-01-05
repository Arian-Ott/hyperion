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

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from starlette.routing  import Mount, Host
from fastapi.middleware.cors import CORSMiddleware

from .core import settings
from .core.redis_db import redis_manager
from .core.startup import startup
from .routers.accounts import account_router
from .routers.dmx import dmx_router
from .routers.fixtures import fixture_router
from .routers.manufacturer import manufacturer_router
from .routers.show import show_router
from .routers.startup_router import startup_router
from .routers.health_check import router as health_router
from .mcp_server import mcp
from mcp.server.sse import SseServerTransport
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

sse = SseServerTransport("/mcp/messages")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle the application lifespan and MCP session manager.

    This context manager ensures that the MCP session manager runs 
    alongside the FastAPI application, providing the necessary 
    infrastructure for SSE and tool execution.

    :param app: The FastAPI application instance.
    """
    # Use the session manager context as shown in the documentation
    
    await startup()
    redis_manager.connect()
    
    yield

    await redis_manager.close()


app = FastAPI(title="Hyperion DMX", debug=settings.DEBUG, lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows GET, POST, OPTIONS, etc.
    allow_headers=["*"],
)
app.include_router(account_router)
app.include_router(dmx_router)
app.include_router(manufacturer_router)
app.include_router(show_router)
app.include_router(fixture_router)
app.include_router(startup_router)
app.include_router(health_router)


@app.get("/mcp/sse", tags=["MCP"])
async def handle_sse(request: Request):
    """
    Handle the SSE connection for the Model Context Protocol.

    This endpoint establishes a Server-Sent Events connection with the 
    client and forwards communication to the Model Context Protocol server.

    :param request: The FastAPI request object.
    :returns: An SSE connection.
    """
    # Use sse.connect_sse to establish the connection with the MCP server.
    # Note: request._send is used to access the underlying ASGI send primitive.
    async with sse.connect_sse(request.scope, request.receive, request._send) as (
        read_stream,
        write_stream,
    ):
        # Run the internal MCP server with the established streams.
        # The attribute name is _mcp_server.
        await mcp._mcp_server.run(
            read_stream,
            write_stream,
            mcp._mcp_server.create_initialization_options(),
        )
app.router.routes.append(
    Mount("/mcp/messages", app=sse.handle_post_message))
if __name__ == "__main__":
    uvicorn.run(
        "src.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG
    )
