from __future__ import annotations

from fastapi import APIRouter, FastAPI
from lib.demo_roster import AGENTS, QUEUES
from lib.schemas.demo import DemoAgentRead, DemoRosterResponse

router = APIRouter()


@router.get("/roster", response_model=DemoRosterResponse)
def get_demo_roster() -> DemoRosterResponse:
    """Return the static demo agents and queues for UI pickers."""
    return DemoRosterResponse(
        agents=[
            DemoAgentRead(
                agent_id=agent.agent_id,
                agent_name=agent.agent_name,
                queue_ids=list(agent.queue_ids),
            )
            for agent in AGENTS
        ],
        queues=sorted(QUEUES),
    )


def register_router(app: FastAPI | APIRouter) -> None:
    """Mount the demo fixture routes on ``app``."""
    app.include_router(router, prefix="/demo", tags=["demo"])
