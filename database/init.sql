-- Runs automatically on first container start (via docker-entrypoint-initdb.d).
--
-- Day 1 scope: enable the pgvector extension only. The actual RAG schema
-- (documents, chunks with embedding columns, conversations, etc.) is
-- deliberately NOT created yet — see backend/app/db/migrations/README.md.
-- It will be added via Alembic migrations starting Day 2, once the
-- chunking/embedding design is finalized.

CREATE EXTENSION IF NOT EXISTS vector;
