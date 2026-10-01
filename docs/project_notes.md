# Project Notes

Running log of what's built vs. planned. Update this as each day's work lands.

## Day 1 — Foundation (this delivery)

- [x] Monorepo structure (frontend, backend, database, docs, scripts)
- [x] Next.js + TypeScript + Tailwind app shell (sidebar, navbar, 7 pages)
- [x] FastAPI app with config, logging, CORS, global error handling
- [x] `GET /health` (real) + `/api/v1/*` routes (honest 501 stubs)
- [x] Async Postgres connection layer (no schema yet)
- [x] Docker Compose for Postgres + pgvector
- [x] `.env.example`, `.gitignore`, README, architecture docs
- [x] Backend tests (health real; others assert honest 501/skip)

## Day 2 — Auth + document upload (this delivery)

- [x] Implement `/api/v1/auth/register` + `/login` + `/me` for real (JWT-based)
- [x] Alembic set up; migration `0001_create_users_table`
- [x] Document upload endpoint + local-disk storage
- [x] Migration `0002_create_documents_table` (owner_id FK, cascade delete)
- [x] Document listing + get-by-id, strictly scoped to owner (404 not 403 for others' docs)
- [x] Wire frontend login/register form to real endpoints (JWT stored in localStorage)
- [x] Wire frontend document upload + list to real endpoints
- [x] Dashboard shows real signed-in user + real document count
- [x] Sidebar shows auth state + sign out from anywhere in the app
- [x] `test_auth.py`, `test_documents.py`, `test_permissions.py` rewritten as real integration tests (require DB)
- [x] `test_security.py` added — self-contained unit tests for hashing/JWT (no DB needed)

## Day 3 — Text extraction + chunking + embeddings (this delivery)

- [x] PDF/DOCX/TXT text extraction (`extraction_service.py`) — real pypdf/python-docx/stdlib implementations
- [x] Chunking strategy finalized (`chunking_service.py`) — fixed-size sliding window, 1000/150 default, logic verified by standalone execution
- [x] Embedding model selected + wired (`embedding_service.py`) — Gemini `text-embedding-004`, 768-dim
- [x] `chunks` table migration (`0003_create_chunks_table.py`) with `vector(768)` column + ivfflat cosine index
- [x] Upload now runs the full pipeline synchronously; `status` becomes `"ready"` or `"failed"`
- [x] `POST /api/v1/documents/{id}/reprocess` — retry after fixing a failure (e.g. adding `GEMINI_API_KEY`)
- [x] `GET /api/v1/documents/{id}/chunks` — inspect what processing produced
- [x] `test_chunking.py`, `test_extraction.py`, `test_embedding.py` added — all pure/mocked, no DB or network needed
- [x] `test_documents.py` extended for the pipeline, tolerant of missing `GEMINI_API_KEY` in test environments

## Day 4 — Retrieval + search (planned)

- [ ] pgvector similarity search (`retrieval_service.py`) — table + ivfflat index already exist (Day 3), just needs the query
- [ ] `/api/v1/search` implemented for real
- [ ] Embed the search query itself (reuse `embedding_service.embed_texts`)

## Day 5 — RAG chat with citations (planned)

- [ ] Gemini API integration for generation
- [ ] `/api/v1/chat` implemented for real, returns grounded answers + citations
- [ ] Frontend chat window wired to real endpoint

## Day 6 — Meetings + decisions (planned)

- [ ] Meeting notes ingestion
- [ ] Decision extraction from documents/meetings
- [ ] `/api/v1/meetings`, `/api/v1/decisions` implemented

## Day 7 — Knowledge gaps + polish (planned)

- [ ] Knowledge gap detection (low-confidence/unanswered questions)
- [ ] `/api/v1/knowledge-gaps` implemented
- [ ] End-to-end pass: fix bugs, tighten UI, final README pass
