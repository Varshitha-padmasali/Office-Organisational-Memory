# Migrations

**Status: not set up yet (planned for Day 2).**

Once the RAG schema (documents, chunks, embeddings, conversations, etc.) is
finalized, we'll initialize Alembic here:

```bash
cd backend
alembic init app/db/migrations
```

For Day 1, the database only needs the `pgvector` extension enabled
(handled by `database/init.sql` via Docker Compose) and the connection
layer in `app/db/database.py`. No tables are created yet.
