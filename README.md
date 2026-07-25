# Intraday Notification System

Assembled is a demo intraday notification system for contact-center operations. Agents and team leads configure alert rules over queue snapshots, agent state, and adherence events; the backend evaluates each event and notifies when a condition becomes true (not on every later poll) so alerts stay timely without spam. Product details, MVP scope, tradeoffs, and roadmap: [PRD.md](PRD.md). Layout: `server/` (FastAPI + evaluator) and `client/` (React + Vite).

## Architecture

```mermaid
flowchart LR
  subgraph Client["client/"]
    UI["React UI"]
  end

  subgraph Gateway["server/gateway"]
    API["FastAPI routers"]
  end

  subgraph Services["server/services"]
    Rules["rules/<br/>RuleService"]
    Ingest["ingest/<br/>IngestService"]
    Notify["notifications/<br/>NotificationService"]

    subgraph Evaluator["evaluator/"]
      Engine["RuleEngine"]
      Index["RuleIndex"]
      Triggers["triggers/"]
    end
  end

  subgraph Data["SQLite"]
    DB[("assembled.db<br/>rules · notifications · notification_dedup")]
  end

  subgraph Harness["demo harness"]
    JSONL["events.jsonl"]
    Replayer["JsonlReplayer"]
  end

  UI -->|"CRUD /rules<br/>poll /notifications"| API
  API --> Rules
  API -->|"POST /events"| Ingest
  API --> Notify

  Ingest --> Rules
  Ingest --> Engine
  Ingest --> Notify

  Engine --> Index
  Engine --> Triggers
  Engine -->|"notification_dedup"| DB
  Rules --> DB
  Notify --> DB

  JSONL --> Replayer
  Replayer -->|"in-process ingest"| Ingest
```

Rules are configured over HTTP; events enter via `POST /events` or the JSONL harness (same `IngestService` + DB as the API). The **evaluator** (`RuleEngine`) indexes enabled rules, runs closed trigger matchers, and remembers prior condition/window state in `notification_dedup` so snapshot feeds notify when a condition becomes true (plus adherence-window dedupe) before `NotificationService` records inbox rows (and console stubs).

## How to run

### Prerequisites

Python 3.12 (pinned in `server/.python-version` for `uv sync`), [uv](https://docs.astral.sh/uv/), [Bun](https://bun.sh/)

### 1. Install dependencies

```bash
cd server && uv sync
cd ../client && bun install
```

`uv sync` installs the app packages (`lib`, `rules`, `evaluator`, `notifications`, `ingest`, `gateway`) editable into the venv — no `PYTHONPATH` export needed.

### 2. Generate the TypeScript API client and trigger form config

```bash
cd server
uv run python scripts/export_openapi.py
uv run export-trigger-config
cd ../client
bun run generate:api
```

Writes `client/src/api-client/` via `openapi-typescript-codegen` (models, enums, and `*Service` classes) and `client/src/routes/rules/triggerFormConfig.generated.ts` from `server/lib/trigger_field_config.py`. App code imports from `@assembled/api-client`, e.g. `RulesService`, `RuleRead`, `TriggerType`. Demo agents/queues are served at runtime by `GET /demo/roster` (from `lib/demo_roster.py`), not codegen’d into the client. Human trigger labels stay in `triggerFormConfig.ts`.

### 3. Seed demo rules (once per empty database)

```bash
cd server
uv run seed-rules
```

Inserts the six built-in demo rules when the rules table is empty. Safe to re-run (no-op if rules already exist). Each seed rule’s `created_by` matches its demo persona (`a_19`, `a_42`, or `lead_billing`) so those usernames see the matching rules in the UI.

### 4. Start the API

```bash
cd server
uv run dev
```

- API: http://127.0.0.1:8000 — Swagger: `/docs`
- Equivalent long form: `uv run uvicorn gateway.main:app --reload --host 127.0.0.1 --port 8000`

### 5. Start the React UI

```bash
cd client
bun run dev
```

- UI typically http://127.0.0.1:5173
- `VITE_API_BASE_URL=http://127.0.0.1:8000`
- Enter a username in the header before creating/editing rules

### 6. Replay the sample morning (instant)

```bash
cd server
uv run python -m tests.event_streamer.jsonl_replayer --events events.jsonl --mode instant
```

### 7. Stream the sample morning (10 wall-clock minutes)

```bash
cd server
uv run stream-events
```

Defaults: `events.jsonl`, stream mode, 600s wall clock. Override as needed, e.g. `uv run stream-events --stream-duration-sec 30`.

### 8. Lint and test

Server (`uv run lint` = ruff check + ruff format --check + mypy):

```bash
cd server
uv run lint
uv run pytest
```

Client (`bun run lint` = Prettier check + ESLint + `tsc --noEmit`):

```bash
cd client
bun run lint
bun test
bun run format   # Prettier --write
bun run typecheck
```

GitHub Actions (`.github/workflows/ci.yml`) runs server lint/pytest, client lint/tests, and fails if `openapi.json` or `triggerFormConfig.generated.ts` are stale.

### 9. Regenerate sample events (optional)

```bash
cd server && uv run python scripts/generate_events.py
```

Note: the JSONL harness under `server/tests/event_streamer` is for demos and tests only; production-shaped ingest is `POST /events`.

## Demo walkthrough (~2–3 min)

With API + UI running and rules seeded:

1. In the UI header, set username to `lead_billing`. Open **Rules** — you should see Billing SLA, backlog ≥ 20, forecast ≥ 130% of recent volume, and long-call rules. Open **Notifications** (empty until replay).
2. In another terminal: `cd server && uv run python -m tests.event_streamer.jsonl_replayer --events events.jsonl --mode instant` (clears prior inbox/dedup, then replays the sample morning).
3. Watch the API terminal for `[NOTIFY]` lines, then refresh/poll **Notifications** as `lead_billing` — expect SLA breach, backlog, forecast-above-recent, and long-call firings.
4. Switch username to `a_19` — inbox shows the adherence > 10m self-alert. Switch to `a_42` — long-call self-alert.
5. Optional: create a rule as either persona (no channel/enabled pickers; delivery is always console + inbox; toggle enable/disable from the rules list).

Story beats come from seed rule ids: `rule_lead_sla_billing`, `rule_lead_tickets_billing`, `rule_lead_forecast_over_volume`, `rule_lead_long_call`, `rule_agent_adherence`, `rule_agent_long_call`.

## Scripts reference

| Where | Command | What it does |
|-------|---------|--------------|
| `server/` | `uv run dev` | API with reload on `:8000` |
| `server/` | `uv run seed-rules` | Insert demo rules if the table is empty |
| `server/` | `uv run stream-events` | Replay `events.jsonl` over ~10 wall-clock minutes |
| `server/` | `uv run lint` | Ruff check, Ruff format check, mypy |
| `server/` | `uv run pytest` | Server tests |
| `server/` | `uv run python scripts/export_openapi.py` | OpenAPI JSON for the client |
| `server/` | `uv run export-trigger-config` | Trigger form field flags → `triggerFormConfig.generated.ts` |
| `server/` | `uv run python scripts/generate_events.py` | Regenerate sample JSONL feeds |
| `client/` | `bun run dev` | Vite UI (usually `:5173`) |
| `client/` | `bun run build` | Typecheck + production build |
| `client/` | `bun run generate:api` | Regenerate `src/api-client/` from OpenAPI (`openapi-typescript-codegen`) |
| `client/` | `bun run lint` | Prettier check, ESLint, TypeScript |
| `client/` | `bun test` | Vitest / Bun unit tests (`parseRuleForm`, etc.) |
| `client/` | `bun run format` | Prettier write |
| `client/` | `bun run typecheck` | `tsc --noEmit` only |

## Database schema

SQLite file: `server/data/assembled.db` (created on API startup). Three tables. `notifications.rule_id` and `notification_dedup.rule_id` are foreign keys to `rules.id` with `ON DELETE CASCADE` (SQLite FK pragma enabled on connect).

If you already have an older DB (e.g. with `cooldown_sec`, `eval_state`, or `audience`), delete `server/data/assembled.db` and re-run `uv run seed-rules` (or let the API recreate an empty file on startup).

### `rules`

Configured alert rules. `owner_id` (notification recipient) is always set to the `X-Username` actor on create — same as `created_by`. Rule list/get/update/delete are scoped to `created_by`; ingest evaluation still loads all enabled rules.

| Column | Type | Notes |
|--------|------|--------|
| `id` | TEXT PK | e.g. `rule_lead_sla_billing` |
| `name` | TEXT | Display name |
| `enabled` | BOOLEAN | Disabled rules are skipped |
| `owner_id` | TEXT | Notification recipient (= creating username) |
| `scope_agent_id` | TEXT NULL | Agent scope (optional) |
| `scope_queue_ids_json` | TEXT NULL | JSON array of queue ids |
| `trigger_type` | TEXT | Closed enum (SLA, tickets, forecast over volume, adherence, state duration) |
| `threshold` | INTEGER NULL | Seconds or ticket count, by trigger |
| `target_state` | TEXT NULL | e.g. `on_call` for long-call rules |
| `severity` | TEXT | `info` \| `warning` \| `critical` |
| `channels_json` | TEXT | JSON array, e.g. `["console","inbox"]` |
| `created_at` / `updated_at` | DATETIME | Server timestamps |
| `created_by` / `updated_by` | TEXT | Creator / last editor; CRUD scoped by `created_by` |

### `notifications`

Inbox rows produced when a rule fires (also mirrored to console when `console` is in channels).

| Column | Type | Notes |
|--------|------|--------|
| `id` | TEXT PK | |
| `rule_id` | TEXT FK → `rules.id` | Indexed; CASCADE on rule delete |
| `recipient_id` | TEXT | Indexed; usually `rules.owner_id` |
| `title` / `body` | TEXT | Human-readable alert |
| `severity` | TEXT | Copied from the rule |
| `entity_key` | TEXT | e.g. `queue:billing` or `agent:a_19` |
| `triggering_event_id` | TEXT | Source event id for traceability |
| `ts` | DATETIME | Event time |
| `delivered_channels_json` | TEXT | JSON array of channels used |

### `notification_dedup`

Prior condition/window memory for ``RuleEngine`` (composite PK). Snapshot feeds notify when a condition becomes true; adherence also dedupes within a violation window. Types: ``NotificationDedup*`` / ``NotificationDedupStore``.

| Column | Type | Notes |
|--------|------|--------|
| `rule_id` | TEXT PK, FK → `rules.id` | CASCADE on rule delete |
| `entity_key` | TEXT PK | Same key space as notifications |
| `last_condition_true` | BOOLEAN | Was the condition true last evaluation? |
| `last_violation_window_id` | TEXT NULL | Adherence window already notified |

ORM models live under `server/lib/models/`.

## AI tools used

Tooling: **Cursor** (agent + planning).

- **Used for:** scaffolding FastAPI/React structure, OpenAPI client wiring, draft trigger evaluators and form field config, parallel codebase exploration while refining scope.
- **Not delegated:** product cuts (agents + leads only; closed triggers; no cooldown DSL), noise-control semantics (become-true + adherence window), and what stayed out of MVP.
- **Verified by:** `uv run pytest` (triggers, noise control, rules CRUD, JSONL replay), `bun run lint` / typecheck, `bun test` (`parseRuleForm`), CI (`.github/workflows/ci.yml`), and manual seed → instant replay → inbox/console story beats.
