# Database

## Status as of Day 2

- **Engine:** PostgreSQL 16 with the `pgvector` extension, run via
  `docker-compose.yml` (image: `pgvector/pgvector:pg16`).
- **Extension setup:** `database/init.sql` runs automatically on first
  container start and enables `CREATE EXTENSION vector`.
- **Connection layer:** `backend/app/db/database.py` — async SQLAlchemy
  engine (`asyncpg` driver) + a `get_db()` FastAPI dependency for
  per-request sessions + `check_db_connection()` used by `/health`.
- **Migrations:** Alembic, configured in `backend/alembic.ini` +
  `backend/app/db/migrations/env.py`. Two migrations exist so far:
  - `0001_create_users_table.py`
  - `0002_create_documents_table.py`

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
  status             varchar(20), default 'uploaded'
  uploaded_at        timestamptz, default now()
```

`documents.status` is always `"uploaded"` today. `"processing"`, `"ready"`,
and `"failed"` are reserved for Day 3, once text extraction exists and can
actually fail or complete.

## Why chunks/embeddings still don't exist

The `chunks` table (with a `pgvector` embedding column), `conversations`,
`messages`, `decisions`, and `knowledge_gaps` are still not created. Chunk
size/overlap strategy and embedding dimensionality need to be decided
first (Day 3) — see `docs/architecture.md` §5 for the original reasoning,
which still holds.

## Local access

```bash
docker exec -it org-memory-postgres psql -U postgres -d org_memory
```

```sql
-- inside psql
\dt                      -- list tables
SELECT * FROM users;
SELECT * FROM documents;
```
