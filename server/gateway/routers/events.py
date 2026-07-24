from __future__ import annotations

from fastapi import APIRouter, Depends, FastAPI
from lib.schemas.events import Event
from lib.schemas.ingest import IngestEventResponse

from gateway.deps import get_ingest_service
from ingest.ingest_service import IngestService

router = APIRouter()


@router.post("", response_model=IngestEventResponse)
def ingest_event(
    event: Event,
    service: IngestService = Depends(get_ingest_service),
) -> IngestEventResponse:
    """Ingest a single domain event and return emitted notification IDs."""
    return service.ingest_event(event)


def register_router(app: FastAPI | APIRouter) -> None:
    """Mount the events routes on ``app``."""
    app.include_router(router, prefix="/events", tags=["events"])
