from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    status: str
    mariadb_connected: bool
    redis_connected: bool
    mcp_active: bool
