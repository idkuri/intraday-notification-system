from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from lib.exceptions import DomainValidationError, NotFoundError
from lib.models.rule import RuleModel
from lib.schemas.enums import TriggerType
from lib.schemas.rules import RuleCreate, RuleRead, RuleScope, RuleUpdate
from sqlalchemy import select
from sqlalchemy.orm import Session


@dataclass(frozen=True, slots=True)
class _TriggerFieldRules:
    """Which rule fields a trigger type requires."""

    require_queue_ids: bool = False
    require_agent_id: bool = False
    require_threshold: bool = False
    require_target_state: bool = False


_TRIGGER_FIELD_RULES: dict[TriggerType, _TriggerFieldRules] = {
    TriggerType.QUEUE_SLA_BREACHED: _TriggerFieldRules(require_queue_ids=True),
    TriggerType.QUEUE_TICKETS_WAITING: _TriggerFieldRules(
        require_queue_ids=True,
        require_threshold=True,
    ),
    TriggerType.ADHERENCE_VIOLATION_DURATION: _TriggerFieldRules(
        require_agent_id=True,
        require_threshold=True,
    ),
    TriggerType.AGENT_STATE_DURATION: _TriggerFieldRules(
        require_threshold=True,
        require_target_state=True,
    ),
}


def _validate_actor(actor: str) -> None:
    if not actor.strip():
        raise DomainValidationError("actor must be non-empty")


def _validate_trigger_fields(
    *,
    trigger_type: TriggerType,
    scope: RuleScope,
    threshold: int | None,
    target_state: object | None,
) -> None:
    rules = _TRIGGER_FIELD_RULES[trigger_type]
    label = trigger_type.value

    if rules.require_queue_ids and not scope.queue_ids:
        raise DomainValidationError("scope.queue_ids is required and must be non-empty")
    if rules.require_agent_id and not scope.agent_id:
        raise DomainValidationError(f"scope.agent_id is required for {label}")
    if rules.require_threshold and (threshold is None or threshold <= 0):
        raise DomainValidationError(f"threshold must be > 0 for {label}")
    if rules.require_target_state and target_state is None:
        raise DomainValidationError(f"target_state is required for {label}")


def _validate_rule_fields(data: RuleCreate) -> None:
    if not data.name.strip():
        raise DomainValidationError("name must be non-empty")
    if not data.owner_id.strip():
        raise DomainValidationError("owner_id must be non-empty")
    _validate_trigger_fields(
        trigger_type=data.trigger_type,
        scope=data.scope,
        threshold=data.threshold,
        target_state=data.target_state,
    )


class RuleService:
    """CRUD and query operations for notification rules."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_rules(self, *, actor: str) -> list[RuleRead]:
        """Return rules created by ``actor``, ordered by name."""
        _validate_actor(actor)
        username = actor.strip()
        rules = self._session.scalars(
            select(RuleModel)
            .where(RuleModel.created_by == username)
            .order_by(RuleModel.name)
        ).all()
        return [rule.to_schema() for rule in rules]

    def get_rule(self, rule_id: str, *, actor: str) -> Optional[RuleRead]:
        """Return a rule owned by ``actor``, or ``None`` if missing/unauthorized."""
        _validate_actor(actor)
        try:
            rule = self._require_owned_model(rule_id, actor=actor)
        except NotFoundError:
            return None
        return rule.to_schema()

    def require_rule(self, rule_id: str, *, actor: str) -> RuleRead:
        """Return a rule owned by ``actor``.

        Raises:
            NotFoundError: When no owned rule exists for ``rule_id``.
        """
        return self._require_owned_model(rule_id, actor=actor).to_schema()

    def _require_owned_model(self, rule_id: str, *, actor: str) -> RuleModel:
        """Load the ORM row owned by ``actor`` or raise ``NotFoundError``."""
        _validate_actor(actor)
        rule = self._session.get(RuleModel, rule_id)
        if rule is None or rule.created_by != actor.strip():
            raise NotFoundError(f"Rule {rule_id} not found")
        return rule

    def create_rule(self, data: RuleCreate, *, actor: str) -> RuleRead:
        """Create a rule after validating trigger-specific fields.

        Args:
            data: Rule payload from the API.
            actor: Username recorded as the author of the change.

        Returns:
            The persisted rule.

        Raises:
            DomainValidationError: When ``data`` or ``actor`` is invalid.
        """
        _validate_actor(actor)
        _validate_rule_fields(data)
        rule = RuleModel.from_create(data, actor=actor.strip())
        self._session.add(rule)
        self._session.flush()
        return rule.to_schema()

    def update_rule(self, rule_id: str, data: RuleUpdate, *, actor: str) -> RuleRead:
        """Apply a partial update to an existing rule owned by ``actor``.

        Args:
            rule_id: ID of the rule to update.
            data: Fields to change; omitted fields keep their current values.
            actor: Username that owns the rule and is recorded as updater.

        Returns:
            The updated rule.

        Raises:
            NotFoundError: When no owned rule exists for ``rule_id``.
            DomainValidationError: When the merged rule would be invalid.
        """
        rule = self._require_owned_model(rule_id, actor=actor)

        existing = rule.to_schema()
        merged = RuleCreate(
            name=data.name if data.name is not None else existing.name,
            enabled=data.enabled if data.enabled is not None else existing.enabled,
            audience=data.audience if data.audience is not None else existing.audience,
            owner_id=data.owner_id if data.owner_id is not None else existing.owner_id,
            scope=data.scope if data.scope is not None else existing.scope,
            trigger_type=(
                data.trigger_type if data.trigger_type is not None else existing.trigger_type
            ),
            threshold=data.threshold if data.threshold is not None else existing.threshold,
            target_state=(
                data.target_state if data.target_state is not None else existing.target_state
            ),
            severity=data.severity if data.severity is not None else existing.severity,
            channels=data.channels if data.channels is not None else existing.channels,
        )
        _validate_rule_fields(merged)

        rule.apply_update(data, actor=actor.strip())
        self._session.flush()
        return rule.to_schema()

    def delete_rule(self, rule_id: str, *, actor: str) -> None:
        """Delete a rule owned by ``actor``.

        Raises:
            NotFoundError: When no owned rule exists for ``rule_id``.
        """
        rule = self._require_owned_model(rule_id, actor=actor)
        self._session.delete(rule)
        self._session.flush()

    def list_enabled_rules(self) -> list[RuleRead]:
        """Return enabled rules ordered by name for event evaluation."""
        rules = self._session.scalars(
            select(RuleModel).where(RuleModel.enabled.is_(True)).order_by(RuleModel.name)
        ).all()
        return [rule.to_schema() for rule in rules]
