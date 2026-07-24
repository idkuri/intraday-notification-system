# ingest

Orchestrates one event through rules → evaluation → notification delivery.

## Role

Thin pipeline for `POST /events` and the JSONL demo harness: load enabled rules, run `RuleEngine`, record/deliver each resulting notification. `reset_state` clears notifications and `notification_dedup` for clean replays.

## Entry point

- `IngestService` — `ingest_event`, `reset_state`

## Wired from

`AppContainer.ingest_service` → `gateway/routers/events.py`. Same container path used by `tests/event_streamer` / `uv run stream-events`.

## Depends on

`rules.RuleService`, `evaluator.RuleEngine`, `notifications.NotificationService`, `lib.schemas.events` / `ingest`.

## Flow

```text
Event
  -> RuleService.list_enabled_rules
  -> RuleEngine.evaluate_event
  -> NotificationService.record_and_deliver (per create)
  -> IngestEventResponse
```

## Key files

| File | Purpose |
|------|---------|
| `ingest_service.py` | Pipeline + reset |
