from sqlalchemy import text

from app.core.database import SessionLocal
from app.core.redis import get_redis


def check_database() -> dict[str, str]:
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "component": "mysql"}
    except Exception as exc:  # pragma: no cover - exercised against real infra
        return {
            "status": "error",
            "component": "mysql",
            "error": exc.__class__.__name__,
        }
    finally:
        db.close()


def check_redis() -> dict[str, str]:
    try:
        get_redis().ping()
        return {"status": "ok", "component": "redis"}
    except Exception as exc:  # pragma: no cover - exercised against real infra
        return {
            "status": "error",
            "component": "redis",
            "error": exc.__class__.__name__,
        }
