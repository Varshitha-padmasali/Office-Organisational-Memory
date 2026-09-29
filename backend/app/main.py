"""
FastAPI application entrypoint.

Day 1 responsibilities handled here:
  - App creation + metadata
  - CORS configuration (frontend origin allowed)
  - Global exception handling (no raw tracebacks leak to clients)
  - Structured logging setup
  - GET /health — liveness + DB connectivity check
  - Versioned router mounting under /api/v1 (routes are stubs for now)
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import auth, chat, decisions, documents, knowledge_gaps, meetings, search
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.db.database import check_db_connection

settings = get_settings()

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s (environment=%s)", settings.PROJECT_NAME, settings.ENVIRONMENT)
    yield
    logger.info("Shutting down %s", settings.PROJECT_NAME)


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="AI-powered Office Organizational Memory (RAG) — API",
    lifespan=lifespan,
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Global error handling ---
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Return a consistent JSON error shape for all HTTPExceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"message": exc.detail, "status_code": exc.status_code}},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all for anything unexpected. Logs the full error server-side but
    never leaks internals (stack traces, DB errors, etc.) to the client.
    """
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": {"message": "Internal server error", "status_code": 500}},
    )


# --- Health check (unversioned, for load balancers / uptime checks) ---
@app.get("/health", tags=["system"])
async def health_check() -> dict:
    db_ok = await check_db_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "database": "connected" if db_ok else "unreachable",
    }


# --- Versioned API routes ---
# All routes below are currently stubs that return HTTP 501 — see each
# module's docstring for its planned implementation day. They are wired up
# now so the API surface, CORS, and error handling can be verified
# end-to-end from Day 1 rather than discovered later.
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(documents.router, prefix=settings.API_V1_PREFIX)
app.include_router(chat.router, prefix=settings.API_V1_PREFIX)
app.include_router(meetings.router, prefix=settings.API_V1_PREFIX)
app.include_router(decisions.router, prefix=settings.API_V1_PREFIX)
app.include_router(search.router, prefix=settings.API_V1_PREFIX)
app.include_router(knowledge_gaps.router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["system"])
async def root() -> dict:
    return {
        "message": f"{settings.PROJECT_NAME} API",
        "docs": "/docs",
        "health": "/health",
        "api_version": settings.API_V1_PREFIX,
    }
