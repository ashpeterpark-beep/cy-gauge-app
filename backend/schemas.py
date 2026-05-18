"""
backend/schemas.py
==================
Pydantic request and response schemas for the CY Gauge Functor API.

Usage in main.py:
    from schemas import RunParams, SweepParams, RunResponse, SweepResponse, HealthResponse
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional


# ─── Shared mesh params (reused by both endpoints) ────────────────────────────

class MeshParams(BaseModel):
    nx: int = Field(3, ge=2, le=5, description="Grid points along x-axis")
    ny: int = Field(3, ge=2, le=5, description="Grid points along y-axis")
    nz: int = Field(2, ge=2, le=4, description="Grid points along z-axis")
    nw: int = Field(2, ge=2, le=4, description="Grid points along w-axis")

    @model_validator(mode="after")
    def check_total_vertices(self) -> "MeshParams":
        total = self.nx * self.ny * self.nz * self.nw
        if total > 400:
            raise ValueError(
                f"Total vertices ({total}) exceeds safety limit of 400. "
                "Reduce grid dimensions."
            )
        return self


# ─── Shared gauge params ──────────────────────────────────────────────────────

class GaugeParams(BaseModel):
    N: int = Field(2, ge=2, le=3, description="U(N) gauge group rank")
    scale: float = Field(
        0.05, ge=0.001, le=0.5, description="Link perturbation scale ε"
    )
    h2: float = Field(
        0.01, ge=0.001, le=0.2, description="Lattice spacing squared h²"
    )
    seed: int = Field(42, ge=0, le=9999, description="RNG seed for reproducibility")


# ─── Request schemas ──────────────────────────────────────────────────────────

class RunParams(MeshParams, GaugeParams):
    """Parameters for POST /api/run — full simulation."""

    n_eigs: int = Field(
        10, ge=2, le=30, description="Number of Dolbeault Laplacian eigenvalues"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "nx": 3, "ny": 3, "nz": 2, "nw": 2,
                "N": 2,
                "scale": 0.05,
                "h2": 0.01,
                "seed": 42,
                "n_eigs": 10,
            }
        }
    }


class SweepParams(MeshParams, GaugeParams):
    """Parameters for POST /api/sweep — wall-crossing sweep over mixing t."""

    mu1: float = Field(0.5, ge=-2.0, le=2.0, description="Split bundle phase μ₁")
    mu2: float = Field(-0.3, ge=-2.0, le=2.0, description="Split bundle phase μ₂")
    steps: int = Field(12, ge=4, le=30, description="Number of t ∈ [0,1] steps")

    @field_validator("steps")
    @classmethod
    def steps_must_be_reasonable(cls, v: int) -> int:
        if v > 25:
            raise ValueError("steps must be ≤ 25 to avoid excessive compute time")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "nx": 3, "ny": 3, "nz": 2, "nw": 2,
                "N": 2,
                "scale": 0.05,
                "h2": 0.01,
                "mu1": 0.5,
                "mu2": -0.3,
                "seed": 42,
                "steps": 12,
            }
        }
    }


# ─── Response schemas ─────────────────────────────────────────────────────────

class MeshInfo(BaseModel):
    """Mesh topology summary returned in responses."""
    nV: int = Field(..., description="Number of vertices")
    nE: int = Field(..., description="Number of edges")
    nF: int = Field(..., description="Number of faces (2-simplices)")


class RunResponse(BaseModel):
    """Response from POST /api/run."""

    mesh: MeshInfo

    # Slope filtration
    slopes: List[float] = Field(..., description="Sorted slope eigenvalues λ₁ ≥ λ₂ ≥ …")

    # Hermitian endomorphism Φ
    phi_trace: float = Field(..., description="Real part of tr(Φ)")
    phi_norm: float = Field(..., description="Frobenius norm ‖Φ‖")

    # Curvature
    curv_norms: List[float] = Field(..., description="Per-face curvature norms ‖F_f‖")
    curv_mean: float = Field(..., description="Mean curvature norm")
    curv_max: float = Field(..., description="Max curvature norm")

    # Gauge algebra
    gauge_algebra_dim: int = Field(..., description="Effective gauge algebra dimension")
    expected_gauge_dim: int = Field(..., description="Expected u(N) dimension = N²")

    # Dolbeault Laplacian spectrum
    dolbeault_eigenvalues: List[float] = Field(
        ..., description="Sorted Dolbeault Laplacian eigenvalues"
    )
    zero_modes: int = Field(..., description="Number of zero modes (eigenvalue < 1e-7)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "mesh": {"nV": 36, "nE": 144, "nF": 216},
                "slopes": [0.00123, -0.00123],
                "phi_trace": 0.0,
                "phi_norm": 0.00174,
                "curv_norms": [0.05, 0.07, 0.04],
                "curv_mean": 0.053,
                "curv_max": 0.07,
                "gauge_algebra_dim": 4,
                "expected_gauge_dim": 4,
                "dolbeault_eigenvalues": [0.0, 0.0, 0.012, 0.015],
                "zero_modes": 2,
            }
        }
    }


class SweepPoint(BaseModel):
    """A single data point in the wall-crossing sweep."""
    t: float = Field(..., description="Mixing parameter t ∈ [0, 1]")
    slopes: List[float] = Field(..., description="Slope eigenvalues at this t")
    gauge_dim: int = Field(..., description="Gauge algebra dimension at this t")
    curv_mean: float = Field(..., description="Mean curvature norm at this t")


class SweepResponse(BaseModel):
    """Response from POST /api/sweep."""
    sweep: List[SweepPoint] = Field(..., description="Ordered sweep results")
    mesh: MeshInfo

    model_config = {
        "json_schema_extra": {
            "example": {
                "sweep": [
                    {"t": 0.0, "slopes": [0.5, -0.5], "gauge_dim": 2, "curv_mean": 0.04},
                    {"t": 0.5, "slopes": [0.1, -0.1], "gauge_dim": 4, "curv_mean": 0.02},
                    {"t": 1.0, "slopes": [-0.5, 0.5], "gauge_dim": 2, "curv_mean": 0.04},
                ],
                "mesh": {"nV": 36, "nE": 144, "nF": 216},
            }
        }
    }


# ─── Health ───────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Response from GET /api/health."""
    status: str = Field("ok", description="Always 'ok' if the service is up")
    version: Optional[str] = Field(None, description="API version string")
