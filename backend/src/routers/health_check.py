from typing import Any, Dict
import logging

from fastapi import APIRouter, Depends, status, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.redis_db import get_redis
from ..core.security.access import require_viewer
from ..mcp_server import mcp
from ..schemas.health_check import HealthCheckResponse

router = APIRouter(tags=["health"])
logger = logging.getLogger("hyperion.health_check.router")


@router.get(
    "/api/health_check",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheckResponse,
)
async def health_check(
    db: AsyncSession = Depends(get_db),
    redis_client=Depends(get_redis),
    response: Response = None,
) -> HealthCheckResponse:
    """Return connection status for MariaDB, Redis and MCP."""
    mariadb_connected, redis_connected, mcp_active = False, False, False
    try:
        result = await db.execute(select(1))
        mariadb_connected = result.scalar_one() == 1
    except Exception:
        logger.error("MariaDB connection failed")

    try:
        redis_connected = bool(await redis_client.ping())
    except Exception:
        logger.error("Redis connection failed")

    try:
        mcp_active = getattr(mcp, "_mcp_server", None) is not None
    except Exception:
        logger.error("MCP server status check failed")

    health_status = HealthCheckResponse(
        status="ok",
        mariadb_connected=mariadb_connected,
        redis_connected=redis_connected,
        mcp_active=mcp_active,
    )

    if not all([mariadb_connected, redis_connected, mcp_active]):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        health_status.status = "error"

    return health_status
