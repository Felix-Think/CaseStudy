from __future__ import annotations

from fastapi import FastAPI

from api_casestudy.core.config import get_settings
from api_casestudy.routers import agent_router, semantic_router


def create_app() -> FastAPI:
    """
    Factory khởi tạo FastAPI cho dịch vụ CaseStudy Agent & Semantic.
    """
    settings = get_settings()

    app = FastAPI(
        title="CaseStudy Agent API",
        version=settings.version,
        description="Dịch vụ quản lý semantic store và điều phối agent cho từng case.",
    )

    app.include_router(semantic_router, prefix="/api")
    app.include_router(agent_router, prefix="/api")
    return app


app = create_app()


@app.get("/healthz")
async def healthcheck() -> dict[str, str]:
    """
    Endpoint kiểm tra tình trạng chạy của service.
    """
    return {"status": "ok"}
