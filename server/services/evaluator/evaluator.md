# Evaluator: adding a new trigger

Triggers are a **closed set**: each `TriggerType` has exactly one `TriggerEvaluator`. `RuleEngine` looks up the evaluator, runs it on candidate rules, then applies become-true / window noise control before emitting a `NotificationCreate`.

Use an existing module as a template (e.g. [`triggers/tickets.py`](triggers/tickets.py) for queue snapshots, [`triggers/adherence.py`](triggers/adherence.py) for agent checks).

## Checklist

### 1. Enum

Add a member to `TriggerType` in [`lib/schemas/enums.py`](../../lib/schemas/enums.py).

If the trigger needs a **new event shape**, also add `EventType` and a Pydantic model in [`lib/schemas/events.py`](../../lib/schemas/events.py) (and teach `EventParser` how to parse it).

### 2. Evaluator class

Create `triggers/<name>.py` with a short `*Evaluator` subclass of `TriggerEvaluator`:

- `trigger_type` -> your new `TriggerType`
- `evaluate(event, rule)`:
  - return `None` if `event` is the wrong type
  - otherwise return a `TriggerMatch` with:
    - `entity_key` — stable id for dedup, e.g. `queue:{id}` or `agent:{id}`
    - `condition_true` — whether the alert condition holds **on this event**
    - `title` / `body` — filled when `condition_true` is true (empty strings when false)
    - `violation_window_id` — optional; set when repeats in the same incident window should not re-notify (see adherence)

When the condition is false, still return a `TriggerMatch` with `condition_true=False` (do not return `None`) so `RuleEngine` can clear become-true memory for snapshot-style feeds.

### 3. Register the evaluator

In [`triggers/__init__.py`](triggers/__init__.py), import the class and append an instance to `TriggerRegistry._evaluators`.

### 4. Rule index (event -> trigger + scope)

Update [`rule_index.py`](rule_index.py):

- Add your `TriggerType` to `_QUEUE_TRIGGERS` or `_AGENT_TRIGGERS` (or introduce a new set if scope rules differ).
- Map it in `_EVENT_TRIGGER_TYPES` under the `EventType`(s) that should consider this trigger.
- Ensure `candidates()` scope matching fits the event (queue id list vs agent/queue overlap).

Without this step, the evaluator never runs.

### 5. Rule validation / form fields

Add a `TriggerFieldConfig` entry for your type in [`lib/trigger_field_config.py`](../../lib/trigger_field_config.py) (`TRIGGER_FIELD_CONFIG`). This drives API validation in `RuleService` and the React create/edit form.

Then regenerate the client module:

```bash
uv run export-trigger-config
```

### 6. Noise control (only if special)

Default in [`rule_engine.py`](rule_engine.py): notify when the condition **becomes** true; while it stays true across later events, stay quiet. Adherence also dedupes on `violation_window_id`.

`AGENT_STATE_DURATION` skips become-true gating because `agent_state_change` is already a transition. If your trigger is similarly one-shot per event, add it next to that exception; otherwise leave the default.

### 7. Tests

Add cases in [`tests/evaluator/test_triggers.py`](../../tests/evaluator/test_triggers.py) (true / false / wrong event type). Add a `RuleService` validation case if you introduced new required fields.

### 8. Frontend + OpenAPI

From `server/`:

```bash
uv run python scripts/export_openapi.py
uv run export-trigger-config
```

From `client/`:

```bash
bun run generate:api
```

That refreshes `@/api-client` enums/models and `triggerFormConfig.generated.ts`. Then add a human label in [`client/src/routes/rules/triggerFormConfig.ts`](../../../client/src/routes/rules/triggerFormConfig.ts) (`TRIGGER_LABELS` only — field flags come from the generated file).

### 9. Verify

```bash
cd server && uv run lint && uv run pytest
cd ../client && bun run lint && bun test
```

## Mental model

```text
Event
  -> RuleIndex.candidates (enabled + event type + scope)
  -> TriggerEvaluator.evaluate -> TriggerMatch | None
  -> RuleEngine._should_notify (become-true / window memory in notification_dedup)
  -> NotificationCreate -> NotificationService
```

Do not put trigger logic in `NotificationService`. Dedup memory is evaluator-owned state, not delivery.
