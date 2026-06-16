import logging

from app.core.config import settings
from app.core.database import Base, engine

# Import all models so Base.metadata can see the development schema when AUTO_CREATE_TABLES is enabled.
from app import models  # noqa: F401

logger = logging.getLogger(__name__)


def init_db() -> None:
    """Optionally create tables for local development.

    Normal environments should use Alembic migrations instead of create_all.
    If the database is unavailable, log a warning without blocking /health or docs.
    """
    if not settings.AUTO_CREATE_TABLES:
        return
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:  # pragma: no cover
        logger.warning("Database auto-create skipped: %s", exc)
