"""Trigger create/edit field visibility and validation rules (UI + API source of truth)."""

from __future__ import annotations

from dataclasses import dataclass

from lib.schemas.enums import TriggerType


@dataclass(frozen=True, slots=True)
class TriggerFieldConfig:
    """Which rule fields a trigger type shows in the UI and requires on create/update."""

    show_agent_id: bool = False
    show_queue_ids: bool = False
    show_threshold: bool = False
    show_target_state: bool = False
    agent_id_required: bool = False
    queue_ids_required: bool = False
    threshold_required: bool = False
    target_state_required: bool = False
    require_agent_or_queues: bool = False


TRIGGER_FIELD_CONFIG: dict[TriggerType, TriggerFieldConfig] = {
    TriggerType.QUEUE_SLA_BREACHED: TriggerFieldConfig(
        show_queue_ids=True,
        queue_ids_required=True,
    ),
    TriggerType.QUEUE_TICKETS_WAITING: TriggerFieldConfig(
        show_queue_ids=True,
        show_threshold=True,
        queue_ids_required=True,
        threshold_required=True,
    ),
    TriggerType.QUEUE_FORECAST_OVER_VOLUME: TriggerFieldConfig(
        show_queue_ids=True,
        show_threshold=True,
        queue_ids_required=True,
        threshold_required=True,
    ),
    TriggerType.ADHERENCE_VIOLATION_DURATION: TriggerFieldConfig(
        show_agent_id=True,
        show_threshold=True,
        agent_id_required=True,
        threshold_required=True,
    ),
    TriggerType.AGENT_STATE_DURATION: TriggerFieldConfig(
        show_agent_id=True,
        show_queue_ids=True,
        show_threshold=True,
        show_target_state=True,
        threshold_required=True,
        target_state_required=True,
        require_agent_or_queues=True,
    ),
}
