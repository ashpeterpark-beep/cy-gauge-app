"""
backend/auth.py
===============
API key authentication for the CY Gauge Functor API.

How it works:
  - Reads API_SECRET_KEY and AUTH_ENABLED from environment variables
  - Clients pass the key in the X-API-Key header
  - Health endpoint is always public
  - Compute endpoints (/api/run, /api/sweep) require the key when AUTH_ENABLED=true

Usage in main.py:
    from auth import require_auth

    @app.post("/api/run", response_model=RunResponse, dependencies=[Depends(require_auth)])
    def run_simulation(p: RunParams): ...

    @app.post("/api/sweep", response_model=SweepResponse, dependencies=[Depends(require_auth)])
    def wall_crossing_sweep(p: SweepParams): ...
"""

import os
import hmac
import logging
from typing import Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

logger = logging.getLogger("cy_gauge.auth")

# ─── Config ───────────────────────────────────────────────────────────────────

_AUTH_ENABLED: bool = os.getenv("AUTH_ENABLED", "false").lower() == "true"
_API_SECRET_KEY: Optional[str] = os.getenv("API_SECRET_KEY")

if _AUTH_ENABLED and not _API_SECRET_KEY:
    raise RuntimeError(
        "AUTH_ENABLED=true but API_SECRET_KEY is not set. "
        "Generate one with: openssl rand -hex 32"
    )

if _AUTH_ENABLED:
    logger.info("API key authentication is ENABLED")
else:
    logger.info("API key authentication is DISABLED (set AUTH_ENABLED=true to enable)")


# ─── Header scheme ────────────────────────────────────────────────────────────

_api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,           # we handle the error ourselves below
    description="Pass your API key in the X-API-Key header",
)


# ─── Validation ───────────────────────────────────────────────────────────────

def _verify_key(provided: Optional[str]) -> bool:
    """
    Constant-time comparison to prevent timing attacks.
    Returns True if the key is valid.
    """
    if not _API_SECRET_KEY or not provided:
        return False
    return hmac.compare_digest(
        provided.encode("utf-8"),
        _API_SECRET_KEY.encode("utf-8"),
    )


# ─── Dependency ───────────────────────────────────────────────────────────────

async def require_auth(api_key: Optional[str] = Security(_api_key_header)) -> None:
    """
    FastAPI dependency. Inject via dependencies=[Depends(require_auth)].

    - If AUTH_ENABLED=false: always passes through (no-op).
    - If AUTH_ENABLED=true: validates X-API-Key header.
      - Missing key  → 401 Unauthorized
      - Wrong key    → 403 Forbidden  (distinct codes help debugging)
    """
    if not _AUTH_ENABLED:
        return  # auth is off — let the request through

    if api_key is None:
        logger.warning("Request rejected: missing X-API-Key header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Include it in the X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if not _verify_key(api_key):
        logger.warning("Request rejected: invalid API key provided")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
        )

    logger.debug("Request authenticated successfully")


# ─── Optional: get current key info (useful for future multi-key support) ─────

async def get_api_key(api_key: Optional[str] = Security(_api_key_header)) -> Optional[str]:
    """
    Softer version — returns the key without raising.
    Useful if you want to allow anonymous access with reduced limits.
    """
    return api_key if _verify_key(api_key) else None

