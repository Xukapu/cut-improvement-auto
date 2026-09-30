from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.services.notification_scheduler import (
    start_notification_scheduler,
    stop_notification_scheduler,
)

settings = get_settings()


class HealthResponse(BaseModel):
    status: str
    application: str
    version: str


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await start_notification_scheduler()

    try:
        yield
    finally:
        await stop_notification_scheduler()


app = FastAPI(
    lifespan=lifespan,
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.docs_enabled else None,
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts,
)

app.include_router(api_router)


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["system"],
    summary="Проверка состояния приложения",
)
def healthcheck() -> HealthResponse:
    return HealthResponse(
        status="ok",
        application=settings.app_name,
        version=settings.app_version,
    )
