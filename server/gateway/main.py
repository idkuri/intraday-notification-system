"""FastAPI application entry point for the Assembled intraday API."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import lib.models  # noqa: F401
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from gateway.container import AppContainer
from gateway.deps import get_container_or_none, set_container
from gateway.routers import register_routers


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Create tables if needed and register the app container."""
    if get_container_or_none() is None:
        container = AppContainer()
        container.db.create_all()
        set_container(container)
    yield


app = FastAPI(title="Assembled Intraday", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    # Vite falls back to 5174+ when 5173 is taken.
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):517\d",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["X-Username", "Content-Type", "*"],
)

register_routers(app)
