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

## Day 2 — Auth + document upload (planned)

- [ ] Implement `/api/v1/auth/login` + `/register` for real
- [ ] Alembic migration for `users` table
- [ ] Document upload endpoint + storage (local disk for MVP)
- [ ] `documents` table migration
- [ ] Wire frontend login form + document upload to real endpoints

## Day 3 — Text extraction + chunking + embeddings (planned)

- [ ] PDF/DOCX/TXT text extraction (`extraction_service.py`)
- [ ] Chunking strategy finalized (`chunking_service.py`)
- [ ] Embedding model selected + wired (`embedding_service.py`)
- [ ] `chunks` table migration with `vector` column

## Day 4 — Retrieval + search (planned)

- [ ] pgvector similarity search (`retrieval_service.py`)
- [ ] `/api/v1/search` implemented for real

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
