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

from .routers.manufacturer import manufacturer_router
from .routers.dmx import dmx_router
from .routers.accounts import account_router
from .routers.show import show_router
from .routers.fixtures import fixture_router
from .core.startup import startup
from .core import settings
from fastapi import FastAPI
import uvicorn
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
app = FastAPI(title="Hyperion DMX", debug=settings.DEBUG)


app.include_router(account_router)
app.add_event_handler("startup", startup)
app.include_router(dmx_router)
app.include_router(manufacturer_router)
app.include_router(show_router)
app.include_router(fixture_router)
if __name__ == "__main__":
    uvicorn.run(
        "src.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG
    )
