from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.services import health_service

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }


@router.get("/health/db")
def database_health_check():
    result = health_service.check_database()
    if result["status"] != "ok":
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=result)
    return result


@router.get("/health/redis")
def redis_health_check():
    result = health_service.check_redis()
    if result["status"] != "ok":
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=result)
    return result
