from __future__ import annotations

from fastapi import APIRouter, Depends, FastAPI, Response, status
from lib.schemas.notifications import NotificationRead

from gateway.deps import get_actor_username, get_notification_service
from notifications.notification_service import NotificationService

router = APIRouter()


@router.get("", response_model=list[NotificationRead])
def list_notifications(
    actor: str = Depends(get_actor_username),
    service: NotificationService = Depends(get_notification_service),
) -> list[NotificationRead]:
    return service.list_notifications(actor)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def clear_inbox(
    actor: str = Depends(get_actor_username),
    service: NotificationService = Depends(get_notification_service),
) -> Response:
    service.clear_for_recipient(actor)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def register_router(app: FastAPI | APIRouter) -> None:
    """Mount the notifications routes on ``app``."""
    app.include_router(router, prefix="/notifications", tags=["notifications"])
