"""
Shared pytest fixtures for the cy-gauge-app test suite.
"""

import numpy as np
import pytest
from fastapi.testclient import TestClient

from main import (
    SimplicialComplex,
    build_torus4d,
    random_suN_links,
    app,
)


# ─── FastAPI client ────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def client() -> TestClient:
    """A single TestClient instance reused for the whole test session."""
    return TestClient(app)


# ─── Mesh fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def small_mesh() -> SimplicialComplex:
    """Minimal 2×2×2×2 torus — fast for unit tests."""
    return build_torus4d(nx=2, ny=2, nz=2, nw=2)


@pytest.fixture(scope="session")
def default_mesh() -> SimplicialComplex:
    """Default 3×3×2×2 torus matching RunParams defaults."""
    return build_torus4d(nx=3, ny=3, nz=2, nw=2)


# ─── Gauge field fixtures ──────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def rng_seed() -> int:
    return 42


@pytest.fixture(scope="session")
def small_links_u2(small_mesh, rng_seed):
    """U(2) random link variables on the small mesh."""
    rng = np.random.default_rng(rng_seed)
    return random_suN_links(small_mesh.nE, N=2, scale=0.05, rng=rng)


@pytest.fixture(scope="session")
def default_links_u2(default_mesh, rng_seed):
    """U(2) random link variables on the default mesh."""
    rng = np.random.default_rng(rng_seed)
    return random_suN_links(default_mesh.nE, N=2, scale=0.05, rng=rng)


# ─── API payload helpers ───────────────────────────────────────────────────────

@pytest.fixture
def minimal_run_payload() -> dict:
    """Smallest valid /api/run payload — fast execution."""
    return {
        "nx": 2, "ny": 2, "nz": 2, "nw": 2,
        "N": 2,
        "scale": 0.05,
        "h2": 0.01,
        "seed": 42,
        "n_eigs": 4,
    }


@pytest.fixture
def minimal_sweep_payload() -> dict:
    """Smallest valid /api/sweep payload — fast execution."""
    return {
        "nx": 2, "ny": 2, "nz": 2, "nw": 2,
        "N": 2,
        "scale": 0.05,
        "h2": 0.01,
        "mu1": 0.5,
        "mu2": -0.3,
        "seed": 42,
        "steps": 4,
    }
