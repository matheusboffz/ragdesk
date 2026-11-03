from datetime import datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response schema for the GET /health endpoint."""

    status: str
    app_name: str
    environment: str
    version: str
    timestamp: datetime
