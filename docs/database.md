# Database

## Day 1 status

- **Engine:** PostgreSQL 16 with the `pgvector` extension, run via
  `docker-compose.yml` (image: `pgvector/pgvector:pg16`).
- **Extension setup:** `database/init.sql` runs automatically on first
  container start and enables `CREATE EXTENSION vector`.
- **Connection layer:** `backend/app/db/database.py` — async SQLAlchemy
  engine (`asyncpg` driver) + a `get_db()` FastAPI dependency for
  per-request sessions + `check_db_connection()` used by `/health`.
- **Schema:** intentionally minimal. Only `users` (see
  `backend/app/models/user.py`) is defined, and it has **no migration
  yet** — it exists as a starting point for Day 2 auth, not as something
  currently created in the database.

## Why no schema yet

The real schema — documents, chunks (with `vector` embedding columns),
conversations, messages, decisions, knowledge gaps — depends on decisions
we haven't made yet: chunk size/overlap strategy, embedding model
dimensionality, and whether conversations need multi-turn context. Writing
the schema before those are settled would likely mean throwing away
migrations. See `docs/architecture.md` §5 for the full reasoning.

## Planned schema (Day 2-3 preview, not yet implemented)

```
users            (id, email, hashed_password, full_name, created_at)
documents        (id, owner_id, filename, status, storage_path, uploaded_at)
chunks           (id, document_id, content, embedding vector(N), chunk_index)
conversations    (id, user_id, created_at)
messages         (id, conversation_id, role, content, created_at)
decisions        (id, document_id, summary, decided_at, extracted_at)
knowledge_gaps   (id, question, asked_at, resolved boolean)
```

This will be formalized via Alembic migrations once finalized — see
`backend/app/db/migrations/README.md`.

## Local access

```bash
docker exec -it org-memory-postgres psql -U postgres -d org_memory
```
