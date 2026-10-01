# Database

## Status as of Day 3

- **Engine:** PostgreSQL 16 with the `pgvector` extension, run via
  `docker-compose.yml` (image: `pgvector/pgvector:pg16`).
- **Extension setup:** `database/init.sql` runs automatically on first
  container start and enables `CREATE EXTENSION vector`.
- **Connection layer:** `backend/app/db/database.py` — async SQLAlchemy
  engine (`asyncpg` driver) + a `get_db()` FastAPI dependency for
  per-request sessions + `check_db_connection()` used by `/health`.
- **Migrations:** Alembic, configured in `backend/alembic.ini` +
  `backend/app/db/migrations/env.py`. Three migrations exist so far:
  - `0001_create_users_table.py`
  - `0002_create_documents_table.py`
  - `0003_create_chunks_table.py`

Run them with:

```bash
cd backend
alembic upgrade head
```

## Current schema

```
users
  id                uuid, primary key
  email             varchar(255), unique, indexed
  hashed_password   varchar(255)
  full_name         varchar(255), nullable
  created_at        timestamptz, default now()

documents
  id                 uuid, primary key
  owner_id           uuid, FK -> users.id (ON DELETE CASCADE), indexed
  filename           varchar(255)   -- collision-safe name on disk
  original_filename  varchar(255)   -- what the user uploaded, for display
  content_type       varchar(100)
  size_bytes         integer
  storage_path       varchar(512)   -- local disk path (see app/utils/file_utils.py)
  status             varchar(20), default 'uploaded'  -- uploaded | ready | failed
  uploaded_at        timestamptz, default now()

chunks
  id            uuid, primary key
  document_id   uuid, FK -> documents.id (ON DELETE CASCADE), indexed
  chunk_index   integer          -- 0-based position within the document
  content       text             -- the chunk's extracted text
  embedding     vector(768)      -- Gemini text-embedding-004 output
  created_at    timestamptz, default now()

  -- ivfflat index on embedding (cosine ops) for Day 4's similarity search
```

`documents.status` lifecycle: `"uploaded"` (file saved) → `"ready"`
(extraction + chunking + embedding all succeeded) or `"failed"` (any step
failed — most commonly a missing `GEMINI_API_KEY`). Processing runs
synchronously inside the upload request today (no background worker), so
`"processing"` is defined in the API schema but never actually observed —
see `docs/architecture.md` §12 for why.

## Why `conversations`/`messages`/`decisions`/`knowledge_gaps` still don't exist

Those depend on decisions not yet made (multi-turn context handling,
decision-extraction prompt design) — see `docs/project_notes.md` for the
Day 4-7 plan.

## Local access

```bash
docker exec -it org-memory-postgres psql -U postgres -d org_memory
```

```sql
-- inside psql
\dt                                  -- list tables
SELECT * FROM users;
SELECT * FROM documents;
SELECT id, document_id, chunk_index, left(content, 60) FROM chunks;

-- sanity-check a similarity search manually (Day 4 will wrap this in code)
SELECT content FROM chunks
ORDER BY embedding <=> (SELECT embedding FROM chunks LIMIT 1)
LIMIT 5;
```
