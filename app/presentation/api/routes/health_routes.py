"""Health Routes."""

from fastapi import APIRouter

from app import __version__
from app.config import get_settings
from app.presentation.api.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=__version__,
        environment=settings.environment,
    )


@router.get("/ready")
async def readiness_check() -> dict:
    return {"ready": True}
