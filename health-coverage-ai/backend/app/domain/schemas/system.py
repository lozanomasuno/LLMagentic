"""System schemas — health and status responses."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel


class ServiceStatus(BaseModel):
    status: Literal["connected", "disconnected", "not_configured"]
    message: Optional[str] = None


class SystemStatusResponse(BaseModel):
    version: str
    environment: str
    status: Literal["operational", "degraded", "down"]
    database: ServiceStatus
    vectorstore: ServiceStatus


class DocumentInfo(BaseModel):
    id: str
    name: str
    status: Literal["indexed", "processing", "error"]
    chunks: int
    indexed_at: Optional[datetime] = None
