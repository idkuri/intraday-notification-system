from enum import Enum


class EventType(str, Enum):
    """Inbound event kinds accepted by the ingest pipeline."""

    QUEUE_SNAPSHOT = "queue_snapshot"
    AGENT_STATE_CHANGE = "agent_state_change"
    ADHERENCE_CHECK = "adherence_check"


class Audience(str, Enum):
    """Who a rule is intended for in the product UI (not used for routing)."""

    AGENT = "agent"
    TEAM_LEAD = "team_lead"


class TriggerType(str, Enum):
    """Closed set of rule trigger kinds the evaluator can match."""

    ADHERENCE_VIOLATION_DURATION = "adherence_violation_duration"
    QUEUE_SLA_BREACHED = "queue_sla_breached"
    QUEUE_TICKETS_WAITING = "queue_tickets_waiting"
    AGENT_STATE_DURATION = "agent_state_duration"


class Severity(str, Enum):
    """Alert severity copied onto fired notifications."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ChannelType(str, Enum):
    """Delivery channels for a notification."""

    CONSOLE = "console"
    INBOX = "inbox"


class AgentState(str, Enum):
    """Workforce agent states used in events and state-duration rules."""

    AVAILABLE = "available"
    ON_CALL = "on_call"
    ON_BREAK = "on_break"
    IN_MEETING = "in_meeting"
    OFFLINE = "offline"
