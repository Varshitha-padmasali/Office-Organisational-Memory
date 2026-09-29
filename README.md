# Office Organizational Memory (RAG) — MVP

An AI-powered system where employees upload organizational documents and
ask natural-language questions, answered with grounded, cited responses
via RAG (Retrieval-Augmented Generation).

**Status: Day 1 of 7 — foundation only.** See `docs/project_notes.md` for
the full day-by-day plan. Nothing described below as "not implemented" is
faked anywhere in the code — see `docs/architecture.md` §4 for why.

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

### 5. Run backend tests

```bash
cd backend
pytest
```

Expected result: tests for `/health`, root, and the stub routes' honest
501 responses pass; `test_rag.py` and `test_permissions.py` are explicitly
skipped (nothing to test yet — see each file's docstring).

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
| Login page                     | 🚧 UI only — backend returns 501           |
| Chat page                      | 🚧 UI only — backend returns 501           |
| Document upload/list           | 🚧 UI only — backend returns 501           |
| Meetings / Decisions / Knowledge Gaps | 🚧 Placeholder pages only           |
| Database schema (beyond `users`) | ⏳ Not created yet (by design — Day 2-3) |

See `docs/api.md` for the full endpoint-by-endpoint status table.

## Documentation

- [`docs/architecture.md`](docs/architecture.md) — why each major decision was made
- [`docs/api.md`](docs/api.md) — endpoint reference and status
- [`docs/database.md`](docs/database.md) — schema plan and connection details
- [`docs/project_notes.md`](docs/project_notes.md) — day-by-day build log
