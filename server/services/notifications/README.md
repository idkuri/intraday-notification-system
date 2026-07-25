# notifications

Persists inbox rows and stub-delivers notifications.

## Role

Takes a `NotificationCreate`, delivers on configured channels (console today), and writes the notification row. List/clear via the API are scoped to `recipient_id` (`X-Username`). `clear_all` + dedup clear remain for demo ingest reset. Does not decide *whether* a rule should fire — that is `evaluator`.

## Entry points

- `NotificationService` — `record_and_deliver`, `list_notifications`, `clear_for_recipient`, `clear_all`, `clear_notification_dedup`
- `channels.py` — `NotificationChannel` / `ConsoleChannel`

## Wired from

`AppContainer.notification_service` → `gateway/routers/notifications.py` (`/notifications`). Also called by `IngestService` after evaluation.

## Depends on

`lib.models.notification` / `notification_dedup`, `lib.schemas.notifications` / `enums`, SQLAlchemy session.

## Key files

| File | Purpose |
|------|---------|
| `notification_service.py` | Persist + deliver + clears |
| `channels.py` | Delivery stubs |
