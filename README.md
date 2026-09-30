# Office Organizational Memory (RAG) — MVP

An AI-powered system where employees upload organizational documents and
ask natural-language questions, answered with grounded, cited responses
via RAG (Retrieval-Augmented Generation).

**Status: Day 2 of 7 — foundation + real auth + document upload.** See
`docs/project_notes.md` for the full day-by-day plan. Nothing described
below as "not implemented" is faked anywhere in the code — see
`docs/architecture.md` §4 for why.

## Tech stack

- **Frontend:** Next.js (App Router), React, TypeScript, Tailwind CSS
- **Backend:** FastAPI, Python
- **Database:** PostgreSQL + pgvector
- **AI (Day 3+):** Gemini API for generation, an embedding model for retrieval
- **Dev:** Docker Compose (database), Git

## Prerequisites

- Node.js 20+ and npm
- Python 3.11+
- Docker + Docker Compose

## Setup

### 1. Clone and configure environment

```bash
cp .env.example backend/.env
cp .env.example .env   # optional, some tools read from repo root
```

Edit `backend/.env` and fill in real values (at minimum `JWT_SECRET`;
`GEMINI_API_KEY` isn't used until Day 3+).

### 2. Start the database

```bash
docker compose up -d
```

This starts PostgreSQL with the `pgvector` extension enabled
(`database/init.sql` runs automatically). Verify it's healthy:

```bash
docker compose ps
```

### 3. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head              # creates the users + documents tables
uvicorn app.main:app --reload --port 8000
```

Verify it's running:

```bash
curl http://localhost:8000/health
```

You should see `{"status": "ok", ..., "database": "connected"}` (or
`"degraded"`/`"unreachable"` if Postgres isn't up yet — the API still
starts and responds either way).

Interactive API docs: http://localhost:8000/docs

### 4. Frontend

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 — it redirects to `/dashboard`, which calls the
backend's `/health` endpoint live and shows the connection status.

### 5. Try the real auth + document upload flow

1. Go to http://localhost:3000/login, click "Need an account? Create one",
   and register.
2. You're redirected to the dashboard, now showing "Signed in as …" with a
   real document count.
3. Go to http://localhost:3000/documents and upload a `.pdf`, `.docx`, or
   `.txt` file (up to 20MB) — it's stored on disk under `data/uploads/`
   and its metadata in Postgres.

### 6. Run backend tests

```bash
cd backend
pytest
```

Expected result:
- `test_health.py`, `test_security.py` — pass with no setup (no DB needed).
- `test_auth.py`, `test_documents.py`, `test_permissions.py` — real
  integration tests against register/login/upload/ownership; **require
  Postgres running** (`docker compose up -d`) and migrations applied
  (`alembic upgrade head`).
- `test_search.py` — still asserts the honest 501 (search isn't built yet).
- `test_rag.py` — still explicitly skipped (nothing to test yet).

## Project structure

```
office-organizational-memory/
├── frontend/        Next.js + TypeScript + Tailwind
├── backend/         FastAPI + Python
├── database/        Postgres init scripts (pgvector setup)
├── data/            Uploads (gitignored) + sample documents for local testing
├── docs/            Architecture, API, database, and planning docs
├── scripts/         One-off dev scripts (seeding, embeddings — Day 2-3+)
├── docker-compose.yml
├── .env.example
└── README.md        (this file)
```

## What works today vs. what's a placeholder

| Area                          | Status                                    |
|--------------------------------|-------------------------------------------|
| `GET /health`                  | ✅ Fully functional                        |
| Frontend ↔ backend connectivity| ✅ Verified live on the dashboard page     |
| App shell (sidebar/nav/layout) | ✅ Fully functional                        |
| Auth (register/login/me, JWT)  | ✅ Fully functional                        |
| Document upload/list/get       | ✅ Fully functional (auth-gated)           |
| Chat page                      | 🚧 UI only — backend returns 501           |
| Meetings / Decisions / Knowledge Gaps | 🚧 Placeholder pages only           |
| Database schema (beyond `users` + `documents`) | ⏳ Not created yet (by design — Day 3) |

See `docs/api.md` for the full endpoint-by-endpoint status table.

## Documentation

- [`docs/architecture.md`](docs/architecture.md) — why each major decision was made
- [`docs/api.md`](docs/api.md) — endpoint reference and status
- [`docs/database.md`](docs/database.md) — schema plan and connection details
- [`docs/project_notes.md`](docs/project_notes.md) — day-by-day build log
