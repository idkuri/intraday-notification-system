from __future__ import annotations

from fastapi import FastAPI

from gateway.routers import events, health, notifications, rules


def register_routers(app: FastAPI) -> None:
    """Attach all HTTP routers to the FastAPI application."""
    health.register_router(app)
    rules.register_router(app)
    notifications.register_router(app)
    events.register_router(app)
