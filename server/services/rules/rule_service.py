from __future__ import annotations

from typing import Optional

from lib.exceptions import DomainValidationError, NotFoundError
from lib.models.notification_dedup import NotificationDedupModel
from lib.models.rule import RuleModel
from lib.schemas.enums import TriggerType
from lib.schemas.rules import RuleCreate, RuleRead, RuleScope, RuleUpdate
from lib.trigger_field_config import TRIGGER_FIELD_CONFIG
from sqlalchemy import delete, select
from sqlalchemy.orm import Session


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
    rules = TRIGGER_FIELD_CONFIG[trigger_type]
    label = trigger_type.value
    has_agent = bool(scope.agent_id and scope.agent_id.strip())
    has_queues = bool(scope.queue_ids)

    if rules.queue_ids_required and not has_queues:
        raise DomainValidationError("scope.queue_ids is required and must be non-empty")
    if rules.agent_id_required and not has_agent:
        raise DomainValidationError(f"scope.agent_id is required for {label}")
    if rules.require_agent_or_queues and not has_agent and not has_queues:
        raise DomainValidationError(
            f"scope.agent_id and/or scope.queue_ids is required for {label}"
        )
    if rules.threshold_required and (threshold is None or threshold <= 0):
        raise DomainValidationError(f"threshold must be > 0 for {label}")
    if rules.target_state_required and target_state is None:
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
            select(RuleModel).where(RuleModel.created_by == username).order_by(RuleModel.name)
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
        username = actor.strip()
        data = data.model_copy(update={"owner_id": username})
        _validate_rule_fields(data)
        rule = RuleModel.from_create(data, actor=username)
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
        username = actor.strip()

        existing = rule.to_schema()
        merged = RuleCreate(
            name=data.name if data.name is not None else existing.name,
            enabled=data.enabled if data.enabled is not None else existing.enabled,
            owner_id=username,
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

        rule.apply_update(data, actor=username)
        # Threshold/scope edits must not keep stale become-true / window memory.
        self._session.execute(
            delete(NotificationDedupModel).where(NotificationDedupModel.rule_id == rule_id)
        )
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
