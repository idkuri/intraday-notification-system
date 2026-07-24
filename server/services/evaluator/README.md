# evaluator

Evaluates enabled rules against one inbound event and decides which notifications to create.

## Role

For each event: index candidate rules by event type + scope, run the closed-set trigger matcher, then apply become-true / adherence-window noise control using `notification_dedup` memory. Emits `NotificationCreate` payloads; does not persist or deliver them.

## Entry points

- `RuleEngine` — orchestrates index → triggers → dedup → creates
- `RuleIndex` — candidate selection
- `TriggerRegistry` / `triggers/*` — one evaluator per `TriggerType`
- `NotificationDedupStore` / `create_notification_dedup_store` — prior condition/window persistence

## Wired from

Not HTTP-exposed. `AppContainer.engine(session)` injects into `IngestService`.

## Depends on

`lib.schemas` (events, rules, notifications, notification_dedup, enums), `lib.models.notification_dedup`. No other services.

## Key files

| File | Purpose |
|------|---------|
| `rule_engine.py` | Evaluate path + `_should_notify` |
| `rule_index.py` | Event → candidate rules |
| `triggers/` | Closed trigger evaluators |
| `notification_dedup_store.py` | SQLAlchemy store for dedup rows |
| `ports.py` | `NotificationDedupStore` ABC |
| `evaluator.md` | **How to add a new trigger** |

## Docs

See [evaluator.md](evaluator.md) for the full checklist when adding a `TriggerType`.
