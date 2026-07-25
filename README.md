# Intraday Notification System

Assembled is a demo intraday notification system for contact-center operations. Agents and team leads configure alert rules over queue snapshots, agent state, and adherence events; the backend evaluates each event with edge detection and cooldowns so alerts stay timely without spam. Product details, MVP scope, tradeoffs, and roadmap: [PRD.md](PRD.md). Layout: `server/` (FastAPI + evaluator) and `client/` (React + Vite).

## How to run

### Prerequisites

Python 3.11+, [uv](https://docs.astral.sh/uv/), Node 20+, [pnpm](https://pnpm.io/)

### 1. Install dependencies

```bash
cd server && uv sync --group dev
cd ../client && pnpm install
```

### 2. Generate the TypeScript API client

```bash
cd server
export PYTHONPATH=packages:services:.
uv run python scripts/export_openapi.py
cd ../client
pnpm run generate:api
```

### 3. Start the API

```bash
cd server
export PYTHONPATH=packages:services:.
uv run uvicorn gateway.main:app --reload --host 127.0.0.1 --port 8000
```

- API: http://127.0.0.1:8000 — Swagger: `/docs` — seed rules on startup

### 4. Start the React UI

```bash
cd client
pnpm run dev
```

- UI typically http://127.0.0.1:5173
- `VITE_API_BASE_URL=http://127.0.0.1:8000`
- Enter a username in the header before creating/editing rules

### 5. Replay the sample morning (instant)

```bash
cd server
export PYTHONPATH=packages:services:.
uv run python -m tests.support.jsonl_replayer --events events.jsonl --mode instant
```

### 6. Stream the sample morning (10 wall-clock minutes)

```bash
cd server
export PYTHONPATH=packages:services:.
uv run python -m tests.support.jsonl_replayer --events events.jsonl --mode stream --stream-duration-sec 600
```

### 7. Lint, typecheck, and test

Server:

```bash
cd server
export PYTHONPATH=packages:services:.
uv run ruff check packages services gateway tests scripts
uv run ruff format --check packages services gateway tests scripts
uv run mypy
uv run pytest
```

Client:

```bash
cd client
pnpm exec tsc --noEmit
```

### 8. Regenerate sample events (optional)

```bash
cd server && uv run python scripts/generate_events.py
```

Note: the JSONL harness under `server/tests/support` is for demos and tests only; production-shaped ingest is `POST /events`.

## AI tools used

AI assisted prototyping and parallel planning; final scope, cuts, and verification were human-owned. Tooling included Cursor.
