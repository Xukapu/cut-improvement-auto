from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel

from app.core.config import get_settings

settings = get_settings()


class HealthResponse(BaseModel):
    status: str
    application: str
    version: str


app = FastAPI(
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
