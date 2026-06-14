from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, users, documents, rag, planner, tasks, eval
from app.core.config import settings
from app.core.init_db import init_db


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="RAG-first postgraduate exam guide and intelligent learning planner.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api_prefix = settings.API_V1_PREFIX
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(users.router, prefix=api_prefix)
    app.include_router(documents.router, prefix=api_prefix)
    app.include_router(rag.router, prefix=api_prefix)
    app.include_router(planner.router, prefix=api_prefix)
    app.include_router(tasks.router, prefix=api_prefix)
    app.include_router(eval.router, prefix=api_prefix)

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()

    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok", "service": settings.PROJECT_NAME}

    return app


app = create_app()
