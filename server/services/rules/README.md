# rules

CRUD and validation for notification rules.

## Role

Owns the configured alert rules operators create in the UI. Validates trigger-specific fields (scope, threshold, `target_state`) before persist. Does not evaluate events or send notifications.

## Entry point

- `RuleService` — list / get / create / update / delete, plus `list_enabled_rules` for ingest

## Wired from

`AppContainer.rule_service` → `gateway/routers/rules.py` (`/rules`).

## Depends on

`lib.models.rule`, `lib.schemas.rules` / `enums`, `lib.trigger_field_config`, `lib.exceptions`, SQLAlchemy session.

## Key files

| File | Purpose |
|------|---------|
| `rule_service.py` | CRUD + `_validate_trigger_fields` (reads `TRIGGER_FIELD_CONFIG`) |

When adding a trigger, add a row in `lib/trigger_field_config.py` and run `uv run export-trigger-config` (see also `evaluator/evaluator.md`).
