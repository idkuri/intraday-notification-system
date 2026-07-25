from __future__ import annotations

from gateway.main import app


def test_demo_roster_endpoint(client) -> None:
    response = client.get("/demo/roster")
    assert response.status_code == 200
    body = response.json()
    assert "billing" in body["queues"]
    assert any(agent["agent_id"] == "a_19" for agent in body["agents"])
    # OpenAPI schema is registered for codegen.
    assert "/demo/roster" in app.openapi()["paths"]
