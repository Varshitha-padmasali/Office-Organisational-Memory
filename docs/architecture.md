# Architecture

This document explains the major architectural decisions made on Day 1 and
why, so the reasoning survives past the initial build.

## 1. Monorepo, not separate repos

`frontend/` and `backend/` live in one repository. For a 7-day solo/small-team
MVP, the coordination overhead of two repos (versioning, cross-repo PRs,
keeping API contracts in sync) isn't worth it. `types/index.ts` on the
frontend is hand-kept in sync with the backend's Pydantic schemas — fine at
this scale; an OpenAPI-generated client would be the next step if the
project grew.

## 2. Next.js (App Router) + FastAPI, talking over plain REST/JSON

- **Next.js App Router** was chosen over Pages Router because it's the
  current recommended default, has simpler layouts (see `app/layout.tsx`
  for the shared sidebar/navbar shell), and supports React Server
  Components if we need them later (e.g., streaming chat responses).
- **FastAPI** was chosen for async-native request handling (important once
  we're calling the Gemini API and Postgres concurrently), automatic
  OpenAPI docs at `/docs`, and Pydantic validation for free.
- The two communicate over plain REST/JSON rather than GraphQL or tRPC —
  simplest option, and the team is more likely to already know it.

## 3. API versioning: `/api/v1`

All feature endpoints are mounted under `/api/v1` (see `app/main.py`).
`/health` and `/` are intentionally **unversioned** — they're
infrastructure/liveness endpoints (used by load balancers, uptime
monitors, Docker healthchecks), not part of the evolving feature API, so
they shouldn't be coupled to API version bumps.

## 4. Every unfinished endpoint returns HTTP 501, not fake data

Per the project's explicit requirement to avoid fake functionality, every
route that isn't built yet (`/api/v1/documents`, `/chat`, `/meetings`,
`/decisions`, `/search`, `/knowledge-gaps`) is registered and reachable,
but returns `501 Not Implemented` with a clear message and the planned
day. This means:
- The frontend can be built against the real API shape from Day 1.
- Nobody (including future-us) mistakes a stub for a working feature.
- `backend/tests/test_*.py` encodes this as an actual regression test —
  when a route is implemented for real, its "expect 501" test should be
  replaced with a real one (this is called out in each test file).

The same principle applies on the frontend: the login form, chat window,
and document upload widget all show an honest "not implemented yet"
message when used, instead of silently doing nothing or faking success.

## 5. Database: PostgreSQL + pgvector, connection layer only (Day 1)

We're using Postgres with the `pgvector` extension so embeddings can live
next to relational data (users, documents, decisions) instead of a
separate vector database — one less moving part for a 7-day build, and
`pgvector` similarity search is fast enough at MVP scale.

**Day 1 deliberately stops at the connection layer**
(`backend/app/db/database.py` — async SQLAlchemy engine, session
dependency, and a `check_db_connection()` health check) plus enabling the
`vector` extension (`database/init.sql`). The actual schema (documents,
chunks with embedding columns, conversations, messages, decisions,
knowledge gaps) is intentionally not created yet, because the chunking
strategy and embedding dimensionality need to be decided first (Day 2-3) —
designing the schema before that would likely mean redoing migrations.

A minimal `User` model exists now (`app/models/user.py`) purely so the
`Base` declarative class has one real model, and so Day 2 auth work has
somewhere to start. It has no migration yet.

## 6. Auth is designed but not wired up

`app/core/security.py` has working, tested password hashing and JWT
helpers. `app/api/dependencies.py` has a `get_current_user` stub. Neither
is connected to a live route yet — `/api/v1/auth/login` and `/register`
return 501. This was a deliberate sequencing choice: building the crypto
primitives now means Day 2 is "wire it up," not "design it from scratch."

## 7. Docker Compose covers Postgres only, for now

Only the database is containerized on Day 1. Frontend (`npm run dev`) and
backend (`uvicorn --reload`) run directly on the host during active
development for the fastest possible iteration loop (hot reload, instant
error feedback) — containerizing them adds rebuild latency that isn't
worth it while the API surface is changing daily. The project structure
(each service in its own top-level folder with its own dependency
manifest) means adding `Dockerfile`s and two more `docker-compose.yml`
services later is straightforward and won't require restructuring.

## 8. Configuration via environment variables only

`backend/app/core/config.py` uses `pydantic-settings` to load all config
from environment variables (with a local `.env` for development,
git-ignored). No secrets are hardcoded anywhere in source. `.env.example`
at the repo root documents every required variable
(`DATABASE_URL`, `GEMINI_API_KEY`, `JWT_SECRET`, `NEXT_PUBLIC_API_URL`)
without real values, so a new developer can `cp .env.example .env` and
knows exactly what to fill in.

## 9. Logging and error handling

- `app/core/logging.py` sets up one consistent log format for the whole
  app at startup, instead of scattered `print()` calls.
- `app/main.py` registers two global exception handlers: one for
  `HTTPException` (consistent `{"error": {...}}` JSON shape) and one
  catch-all for unexpected exceptions (logs the full traceback server-side,
  returns a generic 500 to the client — never leaks internals).

## 10. What's explicitly out of scope for Day 1

- Any real RAG behavior (chunking, embeddings, retrieval, generation).
- Any real authentication/session management.
- File upload handling.
- The full database schema / Alembic migrations.
- Containerizing frontend/backend.

These are sequenced across Days 2-7 — see the root `README.md` for the
day-by-day plan.
