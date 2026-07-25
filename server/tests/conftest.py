from __future__ import annotations

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from lib.db.session import DatabaseSessionManager
from lib.schemas.enums import (
    ChannelType,
    Severity,
    TriggerType,
)
from lib.schemas.rules import RuleRead, RuleScope
from scripts.seed_rules import seed_rules_if_empty

from gateway.container import AppContainer
from gateway.deps import set_container
from gateway.main import app


def make_rule_read(**overrides: object) -> RuleRead:
    defaults: dict[str, object] = {
        "id": "rule_test",
        "name": "Test rule",
        "enabled": True,
        "owner_id": "owner_1",
        "scope": RuleScope(queue_ids=["billing"]),
        "trigger_type": TriggerType.QUEUE_SLA_BREACHED,
        "threshold": None,
        "target_state": None,
        "severity": Severity.WARNING,
        "channels": [ChannelType.CONSOLE, ChannelType.INBOX],
        "created_at": datetime(2026, 1, 1, tzinfo=UTC),
        "updated_at": datetime(2026, 1, 1, tzinfo=UTC),
        "created_by": "test",
        "updated_by": "test",
    }
    defaults.update(overrides)
    return RuleRead.model_validate(defaults)


@pytest.fixture
def db_session():
    manager = DatabaseSessionManager("sqlite:///:memory:")
    manager.create_all()
    session = manager.session_factory()()
    try:
        yield session
        session.commit()
    finally:
        session.close()


@pytest.fixture
def tmp_db_url(tmp_path) -> str:
    return f"sqlite:///{tmp_path / 'test.db'}"


@pytest.fixture
def app_container(tmp_db_url: str) -> AppContainer:
    import lib.models  # noqa: F401

    container = AppContainer(tmp_db_url)
    container.db.create_all()

    session = container.session()
    try:
        seed_rules_if_empty(session)
        session.commit()
    finally:
        session.close()

    return container


@pytest.fixture
def client(app_container: AppContainer) -> TestClient:
    set_container(app_container)
    return TestClient(app)
