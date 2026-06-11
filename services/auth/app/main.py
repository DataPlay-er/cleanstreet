"""
main.py — FastAPI application entry point.

Responsibilities:
  - Create the FastAPI() instance
  - Add middleware (CORS, security headers)
  - Mount the auth router
  - Define startup/shutdown lifecycle events
  - Health check endpoint

Run with:
  uvicorn app.main:app --reload         (development)
  uvicorn app.main:app --host 0.0.0.0   (production, behind Traefik)
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from app.config import settings
from app.router import router

# ─────────────────────────────────────────────────────────────────────────── #
# Logging
# ─────────────────────────────────────────────────────────────────────────── #

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────── #
# Lifespan — startup and shutdown in one place
# ─────────────────────────────────────────────────────────────────────────── #

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────── #
    logger.info("Starting %s [%s]", settings.app_name, settings.environment)
    yield
    # ── Shutdown ─────────────────────────────────────────────────────────── #
    logger.info("Shutting down %s", settings.app_name)


# ─────────────────────────────────────────────────────────────────────────── #
# App instance
# ─────────────────────────────────────────────────────────────────────────── #

app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization":True},
    # SECURITY: Disable /docs and /redoc in production.
    # The auto-generated docs expose your entire API surface.
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
)
bearer_scheme = HTTPBearer()

# ─────────────────────────────────────────────────────────────────────────── #
# CORS Middleware
# ─────────────────────────────────────────────────────────────────────────── #

# SECURITY: CORS controls which browser origins can call this API.
# In production, settings.cors_origins must be set to your actual frontend domain.
# NEVER use allow_origins=["*"] — it allows any website to make requests
# on behalf of your users.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,           # required for cookies / Authorization header
    allow_methods=["GET", "POST"],    # auth service only needs these two
    allow_headers=["Authorization", "Content-Type"],
)


# ─────────────────────────────────────────────────────────────────────────── #
# Security headers middleware
# ─────────────────────────────────────────────────────────────────────────── #

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """
    Add security headers to every response.

    These headers protect against common browser-based attacks.
    They're set here (at the app layer) and should also be set at
    the Traefik layer in production for defence in depth.
    """
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    if settings.is_production:
        # Only over HTTPS in production
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains; preload"
        )
    return response


# ─────────────────────────────────────────────────────────────────────────── #
# Routers
# ─────────────────────────────────────────────────────────────────────────── #

app.include_router(router)


# ─────────────────────────────────────────────────────────────────────────── #
# Health check
# ─────────────────────────────────────────────────────────────────────────── #

@app.get(
    "/health",
    tags=["ops"],
    summary="Service health check",
    include_in_schema=not settings.is_production,
)
async def health() -> dict:
    """
    Used by Docker Compose and Traefik to verify the service is alive.
    Returns 200 when the service is up.
    Does NOT check DB or Redis here — liveness only, not readiness.
    """
    return {"status": "ok", "service": settings.app_name}