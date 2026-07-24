# rules

CRUD and validation for notification rules.

## Role

Owns the configured alert rules operators create in the UI. Validates trigger-specific fields (scope, threshold, `target_state`) before persist. Does not evaluate events or send notifications.

## Entry point

- `RuleService` — list / get / create / update / delete, plus `list_enabled_rules` for ingest

## Wired from

`AppContainer.rule_service` → `gateway/routers/rules.py` (`/rules`).

## Depends on

`lib.models.rule`, `lib.schemas.rules` / `enums`, `lib.exceptions`, SQLAlchemy session.

## Key files

| File | Purpose |
|------|---------|
| `rule_service.py` | CRUD + `_TRIGGER_FIELD_RULES` / `_validate_trigger_fields` |

When adding a trigger, add a row to `_TRIGGER_FIELD_RULES` (see also `evaluator/evaluator.md`).
