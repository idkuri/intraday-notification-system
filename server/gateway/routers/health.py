from __future__ import annotations

from fastapi import APIRouter, FastAPI
from lib.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return a simple liveness probe."""
    return HealthResponse(status="ok")


def register_router(app: FastAPI | APIRouter) -> None:
    """Mount the health routes on ``app``."""
    app.include_router(router, tags=["health"])
