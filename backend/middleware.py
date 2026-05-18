"""
backend/middleware.py
=====================
Custom middleware for the CY Gauge Functor API.

Includes:
  - CORS configuration (reads from env, replaces the hardcoded "*")
  - Rate limiting via slowapi (per-IP on compute endpoints)
  - Request logging (method, path, status, duration)
  - Trusted host enforcement in production

Register in main.py:
    from middleware import register_middleware, limiter
    register_middleware(app)

Then decorate compute endpoints:
    from middleware import limiter
    from fastapi import Request

    @app.post("/api/run", response_model=RunResponse)
    @limiter.limit("10/minute")
    def run_simulation(request: Request, p: RunParams): ...
"""

import os
import time
import logging

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.responses import JSONResponse

# ─── Logger ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("cy_gauge")


# ─── Rate limiter (shared instance, imported by main.py) ──────────────────────

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],          # no global limit; apply per-route
    storage_uri="memory://",    # swap for "redis://..." in production
)


# ─── CORS origins ─────────────────────────────────────────────────────────────

def _parse_origins() -> list[str]:
    """
    Read CORS_ORIGINS from env.
    Falls back to localhost only — never '*' in production.
    """
    raw = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
    return [o.strip() for o in raw.split(",") if o.strip()]


# ─── Rate limit exceeded handler ──────────────────────────────────────────────

async def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    logger.warning("Rate limit exceeded: %s %s from %s", request.method, request.url.path, get_remote_address(request))
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests. Please slow down.",
            "limit": str(exc.detail),
        },
    )


# ─── Request logging middleware ───────────────────────────────────────────────

async def _log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s → %d (%.1fms) [%s]",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        get_remote_address(request),
    )
    return response


# ─── Registration ─────────────────────────────────────────────────────────────

def register_middleware(app: FastAPI) -> None:
    """
    Attach all middleware to the FastAPI app.
    Call this once in main.py before defining routes.

    Order matters — FastAPI applies middleware in reverse registration order,
    so the last one added is the outermost layer.
    """

    # 1. Rate limiter (innermost — runs closest to the route handler)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)
    app.add_middleware(SlowAPIMiddleware)

    # 2. Request logging
    app.middleware("http")(_log_requests)

    # 3. CORS
    origins = _parse_origins()
    logger.info("CORS allowed origins: %s", origins)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],      # only what the API uses
        allow_headers=["Content-Type", "X-API-Key"],
    )

    # 4. Trusted hosts (production guard — skipped in dev)
    app_env = os.getenv("APP_ENV", "development")
    if app_env == "production":
        trusted = os.getenv("TRUSTED_HOSTS", "").split(",")
        trusted = [h.strip() for h in trusted if h.strip()]
        if trusted:
            logger.info("Trusted hosts: %s", trusted)
            app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted)
