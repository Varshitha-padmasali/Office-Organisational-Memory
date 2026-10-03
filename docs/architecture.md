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

## 11. Day 2: auth and document ownership

Day 2 implements the two scaffolds Day 1 deliberately left unwired:
authentication (`app/core/security.py`) and the document upload feature.

**Auth uses stateless JWTs, not server-side sessions.** `/api/v1/auth/login`
and `/register` both return a signed JWT (`sub` = user id) with a fixed
expiry (`ACCESS_TOKEN_EXPIRE_MINUTES`, default 24h). The frontend stores it
in `localStorage` (`frontend/lib/token.ts`) and sends it as
`Authorization: Bearer <token>` on every request. This is the simplest
option for a 7-day MVP — no session table, no server-side revocation
list — at the cost of not being able to revoke a token before it expires.
That trade-off is acceptable for now; a refresh-token or session-table
approach is a reasonable Day 8+ hardening step if this goes past MVP.

**Every document is strictly owned by exactly one user.** `documents.owner_id`
is a required foreign key, and every query in `document_service.py` filters
by it. `GET /api/v1/documents/{id}` returns `404` (not `403`) when a
document exists but belongs to someone else — this is deliberate: a `403`
confirms the document exists, a `404` doesn't. `tests/test_permissions.py`
encodes this as a real, un-skipped test now that there's something to test.

**Uploads go straight to local disk, not cloud storage.** Files are saved
under `data/uploads/` (configurable via `UPLOAD_DIR`) with a random
UUID-based filename; the user-facing name is kept separately in
`Document.original_filename`. For a 7-day local MVP this avoids taking a
dependency on S3/GCS credentials and IAM setup that would eat into build
time without changing anything about how the RAG pipeline (Day 3+) reads
the files. `document_service.save_upload_bytes()` is the single seam to
change if/when this needs to move to cloud storage later.

**Upload validation is intentionally minimal but real.** Extension
allowlist (`.pdf`, `.docx`, `.txt`), a size cap (`MAX_UPLOAD_SIZE_MB`,
default 20MB), and an empty-file check happen in the route before
anything touches disk or the database. Virus scanning, MIME-sniffing
beyond the browser-supplied `Content-Type`, and per-user storage quotas
are out of scope for the MVP.

**The frontend's `lib/token.ts` is split out from `lib/auth.ts`
specifically to avoid a circular import**: `lib/api.ts` needs the token to
attach the `Authorization` header, and `lib/auth.ts`'s `useAuth()` hook
calls into `lib/api.ts` (for `getCurrentUser()`) — so the token
get/set/clear functions live in a third, dependency-free module that both
can import.

## 12. Day 3: extraction, chunking, and embeddings

**Processing runs synchronously inside the upload request — no task
queue.** `POST /api/v1/documents/upload` saves the file, then immediately
calls `document_service.process_document()`, which extracts text, chunks
it, embeds every chunk via Gemini, and stores the chunks — all before the
HTTP response is sent. For an MVP where uploads are a handful of small
files (≤20MB, mostly text-dominant PDFs/DOCXs), this keeps the system
simple (no Celery/RQ, no job status polling, no worker process to deploy)
at the cost of upload requests taking a few seconds instead of being
instant. If this needs to handle larger files or higher volume later, the
natural evolution is to make `process_document()` a background task
(FastAPI's `BackgroundTasks` first, a real queue if needed) and have
`status` actually pass through `"processing"` as an observable state —
the schema already has that status value reserved for exactly this.

**A failed pipeline doesn't fail the upload.** `process_document()`
catches every exception internally and sets `status = "failed"` rather
than raising. The most common failure mode by far is a missing
`GEMINI_API_KEY` — a developer who hasn't configured one yet should still
be able to upload and browse files, just without them being searchable
yet. `POST /api/v1/documents/{id}/reprocess` exists specifically so a
developer can add the key and retry without re-uploading.

**Chunking is a simple fixed-size sliding window (1000 chars, 150 overlap),
not sentence- or paragraph-aware.** This was chosen because: (a) it's
trivial to reason about and test deterministically (see
`tests/test_chunking.py`'s exact-overlap test), (b) it has no dependency
on a sentence-boundary library that might mis-segment organizational
jargon/abbreviations, and (c) retrieval quality from fixed-size chunking
is a reasonable baseline — if Day 4's search results are noticeably worse
than expected, smarter chunking (paragraph-aware, or using the embedding
model's own token count instead of characters) is the first thing to
revisit, with the chunk_size/overlap already exposed as function
parameters to make that change localized to one file.

**Embedding model: Gemini `text-embedding-004`, called once per chunk.**
Chosen for consistency with the project's existing choice of Gemini for
generation (one API key, one vendor, one place to look at
quota/billing). Calling the API once per chunk rather than batching
trades some latency for simplicity and avoids depending on batch-endpoint
behavior that varies across client library versions — acceptable since
MVP documents produce a handful of chunks each. `EMBEDDING_DIMENSIONS = 768`
is defined once (`app/models/chunk.py`) and imported by both the
embedding service (to validate what the API actually returned) and the
migration (to size the `vector` column) — if the model ever changes,
both call sites fail loudly instead of silently storing truncated or
padded vectors.

**The `chunks` table gets an `ivfflat` cosine-similarity index up front**
(migration `0003`), even though nothing queries it until Day 4. Creating
it now, on an empty table, means Day 4 doesn't need its own migration just
to add an index — it only needs to write the `SELECT ... ORDER BY
embedding <=> :query_vector` query itself.

## 13. Day 4: semantic search

**Search is scoped to the caller's own `"ready"` documents — the same
ownership model as documents.** `retrieval_service.search_chunks()` joins
`chunks` to `documents` and filters on both `owner_id` and
`status = "ready"` in the same query, rather than searching everything and
filtering after. This means a document stuck in `"failed"` (e.g. no
`GEMINI_API_KEY` was set at upload time) correctly never appears in search
results — it has no chunks to match anyway, but the explicit status filter
also protects against a future bug where a `"failed"` document somehow
has stale chunks left over from a prior successful run.

**The query is embedded with `task_type="retrieval_query"`, not
`"retrieval_document"`.** Gemini's embedding model supports asymmetric
retrieval: the thing being searched for and the things being searched
through are embedded with slightly different task hints, which
empirically improves ranking versus embedding both the same way. Getting
this pairing right now (rather than using `"retrieval_document"`
everywhere for simplicity) costs nothing extra in code and avoids a
retrieval-quality regression that would be easy to miss until Day 5's
generated answers started looking off.

**A missing `GEMINI_API_KEY` surfaces as `503`, not `200` with empty
results or a `500`.** Search always has to embed the incoming query, so if
embeddings aren't configured, the request genuinely cannot be fulfilled —
that's a server-side configuration problem (503 Service Unavailable), not
"nothing matched" (which would be a misleading `200`) or an unhandled
crash (`500`). The frontend's Chat page surfaces this 503's message
directly so a developer immediately knows why search isn't working,
rather than silently showing "no results found."

**The Chat page calls real search now, but deliberately shows raw passages
with no synthesized summary sentence.** It would be easy to template
something like `"Based on your documents, the answer is: {top
result}"` — but that's not what happened; no LLM read these passages and
wrote that sentence. Doing so would violate the project's core "no fake
functionality" rule as surely as a mocked API response would. Instead,
each "assistant" turn is explicitly labeled as search results and renders
the matches as citations (reusing the existing `SourceCitation`
component). Day 5 replaces this with an actual call to Gemini to generate
a grounded answer from the same retrieved passages — at that point the
citations become support *for* a written answer instead of *being* the
answer.

## 14. Day 5: generation

**The LLM is never called when retrieval finds nothing.** If
`retrieval_service.search_chunks()` returns an empty list,
`rag_service.answer_question()` returns a fixed, honest message
("I couldn't find anything relevant...") without touching Gemini at all.
This is the single most important decision in this module: an LLM asked
to answer a question with no supporting context will often still produce
a fluent-sounding answer anyway, drawing on its general training data
instead of the organization's actual documents - which is precisely the
failure mode a RAG system exists to prevent. Short-circuiting before the
call is a stronger guarantee than instructing the model not to do this in
the prompt, because it doesn't depend on the model reliably following
that instruction.

**The prompt instructs the model to answer ONLY from the provided
context, and to say so plainly if the context is insufficient** (see
`app/prompts/rag_prompt.txt`). This is a second layer of defense, not the
primary one - the primary one is the empty-results short-circuit above.
Even with results present, the retrieved chunks might not actually
contain the answer (e.g. they're topically related but don't cover the
specific question), so the model still needs instructions for that case.

**Chat is a `POST`, not a `GET` like search.** Both endpoints take a
query string in some form, but generation is a costly, side-effecting
external API call (billed, rate-limited, non-idempotent in the sense that
re-running it costs money again) rather than a cheap idempotent lookup.
`POST` also leaves room for a request body to grow (e.g. a future
`conversation_id` for multi-turn context) without the awkwardness of
stuffing more fields into query parameters.

**`build_prompt()` is a standalone, pure function, not inlined into
`answer_question()`.** It takes the question and retrieved results and
returns a string - no I/O, no network, no database. This is what makes
`tests/test_rag.py` able to verify the prompt's structure (correct source
numbering, question included, chunk content included) without mocking
anything beyond that function's direct inputs, and separately what makes
the orchestration logic (when to call the LLM, how failures are handled)
testable by mocking only `retrieval_service.search_chunks` and the Gemini
SDK calls - the two actually-expensive operations.

**Generation failures are caught and re-raised as a dedicated
`GenerationError`,** mirroring `EmbeddingError`'s role in Day 3-4. The
chat route catches both and maps them to `503` - a generation failure
(timeout, API error, malformed response) is a server-side problem with an
external dependency, not something the client did wrong, so `503` is the
honest status code, the same reasoning applied to search in Day 4.

**The chat model (`GEMINI_CHAT_MODEL`) is configurable via settings, while
the embedding model is not.** The embedding model's output dimension is
load-bearing - it has to match `EMBEDDING_DIMENSIONS` and the `chunks`
table's `vector` column width, so changing it requires a migration, not
just a config edit (see section 12). The chat model has no such
constraint: any model that implements the same `generate_content`
interface can be swapped in via `.env` without touching the database.

## 15. Day 6: meetings and decisions

**A decision always belongs to exactly one source (a meeting or a
document), enforced at two levels.** `decisions.meeting_id` and
`decisions.document_id` are both nullable foreign keys, and a database
CHECK constraint (`ck_decisions_exactly_one_source`, migration 0005)
guarantees exactly one is set on every row - not "at least one," exactly
one. `decision_service.create_decisions()` also refuses at the
application level before even reaching the database. Two layers instead
of one: the application check gives a clear Python-level error during
development; the database constraint is what actually protects the data
if some future code path bypasses the service layer.

**Meeting processing (summarize + extract decisions) is synchronous and
automatic on create, mirroring document upload from Day 3** - same
reasoning: MVP scale, no task queue yet, and a failure degrades the
meeting to `status: "failed"` rather than losing the raw notes, which are
saved before any LLM call happens.

**Document decision extraction is the opposite: explicit and opt-in**,
via `POST /api/v1/documents/{id}/extract-decisions`, not run automatically
on upload. Documents are already paying for one synchronous LLM-adjacent
pipeline at upload time (extract, chunk, embed - Day 3); adding decision
extraction as a second mandatory step would mean every single upload,
including ones with no decisions in them at all (most documents), pays
the latency and Gemini cost of an extra generation call. Meetings don't
have this problem because they're typically short, so summarizing and
extracting decisions together is cheap. The trade-off is visible in the
UI: documents get an "Extract decisions" button the user presses when
they expect it's worth it, meetings get decisions "for free."

**Decision extraction asks Gemini for JSON, not prose, and the parsing is
written defensively.** The prompt (`app/prompts/decision_prompt.txt`)
asks for a plain JSON array with no markdown fences, but
`decision_service._strip_code_fences()` strips them anyway if the model
adds them - which, empirically, LLMs asked for JSON often do despite
being told not to. Malformed JSON, a non-array response, or array items
missing the required `summary` field all fail predictably
(`DecisionExtractionError` for the first two, silently skipped for the
third) rather than crashing or inserting garbage rows. This logic was
verified by extracting it into a standalone script and running it against
nine cases (plain JSON, `json`-fenced, bare-fenced, empty array, multiple
items, a missing-field item, and malformed input) before it went into the
service.

**`DecisionOut` is built by a service-layer function
(`decision_service.to_decision_out()`), not a Pydantic `from_attributes`
mapping straight off the ORM row.** A `Decision` row only stores
`meeting_id` or `document_id` - it doesn't know the meeting's title or the
document's filename. Rather than make every caller do a second lookup (or
worse, have the frontend do N+1 requests to resolve titles), both list
and get queries use `outerjoin`s against `meetings` and `documents` to
fetch the title in the same query, and `to_decision_out()` collapses the
two nullable source columns plus the resolved title into the single
`source_type`/`source_id`/`source_title` trio the API actually exposes.
