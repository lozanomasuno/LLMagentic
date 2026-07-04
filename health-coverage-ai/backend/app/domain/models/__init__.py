"""ORM models — imported here so Alembic detects all tables."""

from app.domain.models.affiliate import Affiliate
from app.domain.models.consultation import Consultation
from app.domain.models.log import Log

__all__ = ["Affiliate", "Consultation", "Log"]
