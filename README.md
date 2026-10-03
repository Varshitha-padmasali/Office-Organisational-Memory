# Office Organizational Memory (RAG) - MVP

An AI-powered system where employees upload organizational documents and
ask natural-language questions, answered with grounded, cited responses
via RAG (Retrieval-Augmented Generation).

**Status: Day 6 of 7 - foundation, auth, document upload, extraction,
chunking, embeddings, semantic search, generated chat answers, meeting
notes ingestion, and decision extraction are all real and working.** See
`docs/project_notes.md` for the full day-by-day plan. Nothing described
below as "not implemented" is faked anywhere in the code - see
`docs/architecture.md` section 4 for why.

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

Edit `backend/.env` and fill in real values. `JWT_SECRET` is required for
auth. `GEMINI_API_KEY` is used to embed uploaded documents (Day 3) and to
generate chat answers (Day 5) - get one at
https://aistudio.google.com/app/apikey. Without it, uploads still work but
documents end up with `status: "failed"` (file is saved, just not yet
searchable) - add the key and call `POST /api/v1/documents/{id}/reprocess`
to retry.

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
`"degraded"`/`"unreachable"` if Postgres isn't up yet - the API still
starts and responds either way).

Interactive API docs: http://localhost:8000/docs

### 4. Frontend

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 - it redirects to `/dashboard`, which calls the
backend's `/health` endpoint live and shows the connection status.

### 5-6. Try the real auth + document upload + search + meetings/decisions flow

1. Go to http://localhost:3000/login, click "Need an account? Create one",
   and register.
2. You're redirected to the dashboard, now showing "Signed in as …" with a
   real document count.
3. Go to http://localhost:3000/documents and upload a `.pdf`, `.docx`, or
   `.txt` file (up to 20MB) - it's stored on disk under `data/uploads/`,
   and (if `GEMINI_API_KEY` is set) immediately extracted, chunked, and
   embedded. Check `GET /api/v1/documents/{id}/chunks` in the API docs
   (http://localhost:8000/docs) to see the chunks it produced.
4. Go to http://localhost:3000/chat and ask a question related to what you
   uploaded - you'll get back a real generated answer from Gemini, grounded
   only in your own documents, with the source passages shown below as
   citations (each with a relevance score). Ask something unrelated to
   anything you've uploaded and it will say it couldn't find anything
   relevant, rather than guessing.
5. Go to http://localhost:3000/meetings and log some notes containing a
   clear decision (e.g. "We decided to renew the vendor contract for
   another year."). The notes are summarized automatically, and the
   decision shows up on http://localhost:3000/decisions.
6. Back on http://localhost:3000/documents, click "Extract decisions" on
   a `"ready"` document to pull any decisions out of it the same way.

### 7. Run backend tests

```bash
cd backend
pytest
```

Expected result:
- `test_health.py`, `test_security.py`, `test_chunking.py`,
  `test_extraction.py`, `test_embedding.py`, `test_rag.py`,
  `test_decision_extraction.py` - pass with no setup (no DB, no network,
  no API key needed - the Gemini calls are mocked throughout).
- `test_auth.py`, `test_documents.py`, `test_permissions.py`,
  `test_search.py`, `test_chat.py`, `test_meetings.py`,
  `test_decisions.py` - real integration tests; **require Postgres
  running** (`docker compose up -d`) and migrations applied (`alembic
  upgrade head`). Status/result assertions accept whichever outcome is
  correct for whether a real `GEMINI_API_KEY` is configured in your
  environment (`"ready"`/`"summarized"` vs `"failed"`, populated results
  vs `503`) - see each file's docstring.

## Project structure

```
office-organizational-memory/
├── frontend/        Next.js + TypeScript + Tailwind
├── backend/         FastAPI + Python
├── database/        Postgres init scripts (pgvector setup)
├── data/            Uploads (gitignored) + sample documents for local testing
├── docs/            Architecture, API, database, and planning docs
├── scripts/         One-off dev scripts (seeding, embeddings - Day 2-3+)
├── docker-compose.yml
├── .env.example
└── README.md        (this file)
```

## What works today vs. what's a placeholder

| Area                           | Status                                    |
|--------------------------------|--------------------------------------------|
| `GET /health`                  | Fully functional                           |
| Frontend/backend connectivity  | Verified live on the dashboard page        |
| App shell (sidebar/nav/layout) | Fully functional                           |
| Auth (register/login/me, JWT)  | Fully functional                           |
| Document upload/list/get       | Fully functional (auth-gated)              |
| Text extraction (PDF/DOCX/TXT) | Fully functional                           |
| Chunking                       | Fully functional                           |
| Embeddings (Gemini)            | Fully functional (needs `GEMINI_API_KEY`)  |
| Semantic search                | Fully functional (needs `GEMINI_API_KEY`)  |
| Chat with generated answers    | Fully functional (needs `GEMINI_API_KEY`)  |
| Meeting notes + summarization  | Fully functional (needs `GEMINI_API_KEY`)  |
| Decision extraction (meetings + documents) | Fully functional (needs `GEMINI_API_KEY`) |
| Knowledge Gaps                 | Placeholder page only (Day 7)              |
| Database schema (beyond `users`/`documents`/`chunks`/`meetings`/`decisions`) | Not created yet (Day 7) |

See `docs/api.md` for the full endpoint-by-endpoint status table.

## Documentation

- [`docs/architecture.md`](docs/architecture.md) - why each major decision was made
- [`docs/api.md`](docs/api.md) - endpoint reference and status
- [`docs/database.md`](docs/database.md) - schema plan and connection details
- [`docs/project_notes.md`](docs/project_notes.md) - day-by-day build log
