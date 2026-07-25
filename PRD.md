# Intraday Notifications — PRD

Contact-center ops need timely intraday alerts when queues slip, agents go out of adherence, or calls run long — without the noise of repeated firings on every snapshot. This MVP lets agents and team leads configure closed trigger types, evaluates a live-style event stream, and surfaces firings in an inbox with enough traceability to trust the demo.

## Goals

- Let agents and team leads configure intraday alert rules scoped to themselves or their queues.
- Evaluate incoming queue, agent-state, and adherence events with noise control (rising edge, adherence-window dedupe, cooldowns).
- Make firings visible and traceable via the notifications inbox and console delivery stub.

## Users

- **Agent** — personal adherence and long-call self-alerts (e.g. “my adherence violation > 10m”, “my call > 45m”).
- **Team lead** — queue SLA breaches, backlog thresholds, and long calls on owned queues.
- Not optimizing for head-of-support digests or forecast-driven alerts in this MVP.

## MVP scope

### In scope

- Rule configuration via React UI + JSON API with four closed triggers: adherence violation duration, queue SLA breach, tickets waiting, agent state duration (long call).
- Per-event evaluation with edge detection, adherence-window dedupe, and cooldowns.
- Stub delivery: console log + DB inbox; notifications UI with 3s polling.
- Username stub for `created_by` / `updated_by` (not real auth).
- Seed rules plus a ~90-minute / ~100-event sample morning feed.
- Demo JSONL harness (instant replay + 10-minute stream) as an engineering aid, not a product surface.

### Out of scope

- Real Slack, email, or push delivery.
- Authentication, authorization, or multi-tenancy.
- Production deploy, CI/CD, or infra-as-code.
- Free-form rule DSL or drag-and-drop builder.
- Head-of-support digests; forecast-based alerts.
- Kafka, Redis, websockets, or multi-process deploy.
- Treating the JSONL replayer as a customer-facing product.

## Product decisions

- **Audiences** — Agents get self-scoped rules; team leads get queue-scoped rules. `owner_id` is the notification recipient; scope fields (`agent_id`, `queue_ids`) limit which events a rule can match.
- **Noise control** — Triggers fire on rising edges where applicable; adherence violations dedupe within a window; all triggers respect per-rule cooldowns. State-duration triggers use cooldown-only gating (no rising edge).
- **Closed triggers** — Four typed evaluators instead of an expression language keeps the MVP reviewable, testable, and UI-friendly without building a DSL parser.
- **Username stub** — The UI sends `X-Username` for audit fields on rule CRUD. There is no login; usernames are a stand-in until real auth exists.
- **Delivery stub** — Notifications persist to SQLite and print to console. External channels plug in behind the same delivery port later.

## Tradeoffs

- **Python MVP vs Go for a hotter ingest path** — CPython’s GIL prevents *parallel* Python bytecode across threads (CPU-bound multi-threading won’t use multiple cores). I/O concurrency is real via asyncio/FastAPI. For this product’s typical work (cheap rule checks plus DB/network), the limit is usually I/O and noise-control design, not the GIL — even “millions of events/day” is modest average QPS. Go still helps when you want denser multi-core CPU eval, cheaper goroutines, and channel-style in-process pipelines for a dedicated stream worker. This MVP uses Python for speed-to-demo (FastAPI, Pydantic, SQLAlchemy, OpenAPI→TS), not because Python cannot concurrent-handle the demo.
- **In-process gateway vs separately deployed services** — Rules, evaluator, notifications, and ingest run in one FastAPI process for simplicity. A real deployment would split ingest/eval/dispatch workers once scale or blast radius demands it.
- **SQLite vs Postgres/Redis** — SQLite keeps the take-home zero-config. Postgres plus Redis (or similar) for eval state would be the production path under concurrent writers and HA requirements.
- **Polling vs websockets** — The notifications page polls every 3 seconds. Simple and sufficient for demo scale; websockets or SSE would reduce chatter at higher fan-out.
- **Closed triggers vs expression language** — Faster to ship and easier to test, at the cost of flexibility for power users.
- **Username stub vs real auth** — Unblocks rule CRUD audit fields without OAuth/session work.
- **Generated OpenAPI client vs hand-written DTOs** — Single source of truth from Pydantic models; requires regenerating when the API changes.

## What I'd do with more time

- **If/when profiling shows CPU/eval or connection-density limits:** extract ingest/evaluator/dispatch to a Go worker (channels + shard-by-entity); keep React + OpenAPI stable. Until then, scale the Python boundary with async workers/processes.
- Real Slack/email behind the same delivery port.
- Richer rule builder plus “would this have fired?” preview.
- Replace username stub with real auth and authz.
- Postgres + Redis eval state; shard ingest by entity.
- Forecast / head-of-support digests.
- Outbox + async delivery; websocket push.
- CI freshness check for OpenAPI / `schema.ts`.

## Success criteria for the demo

- Configure a rule in the UI with a username set.
- Replay or stream the sample feed; correct notifications for seed story beats (SLA breach, backlog, adherence, long call).
- Each notification is traceable via `rule_id` and the triggering event context.

## Assumptions

- Single-tenant demo; no auth beyond the username header stub.
- Event feed is JSONL locally; production would POST events to `/events` or a bus consumer.
- SQLite file DB is acceptable for concurrent demo load (brief locks under stream + API reads).
- Seed rules and sample events encode a coherent “morning shift” narrative for reviewers.
- Reviewers run server and client locally; no hosted environment is provided.
