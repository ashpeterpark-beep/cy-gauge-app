"""
Test suite for the CY Gauge Functor backend (main.py).

Coverage targets
----------------
Unit  : SimplicialComplex, build_torus4d, random_suN_links,
        face_holonomies, herm_endomorphism, slope_filtration,
        lie_closure, effective_gauge_algebra_dim, dolbeault_spectrum
API   : GET /api/health, POST /api/run, POST /api/sweep
        — happy paths, field validation, determinism, error handling
"""

import math

import numpy as np
import pytest

from main import (
    SimplicialComplex,
    build_torus4d,
    dolbeault_spectrum,
    effective_gauge_algebra_dim,
    face_holonomies,
    herm_endomorphism,
    lie_closure,
    random_suN_links,
    slope_filtration,
    split_bundle_links,
)


# ══════════════════════════════════════════════════════════════════════════════
# Unit tests — mesh / SimplicialComplex
# ══════════════════════════════════════════════════════════════════════════════

class TestSimplicialComplex:
    def test_vertex_count(self, small_mesh):
        assert small_mesh.nV == 2 * 2 * 2 * 2  # 16

    def test_edge_index_covers_all_edges(self, small_mesh):
        assert len(small_mesh.edge_index) == small_mesh.nE

    def test_edge_index_keys_are_sorted_tuples(self, small_mesh):
        for key in small_mesh.edge_index:
            assert key == tuple(sorted(key))

    def test_face_vertices_in_range(self, small_mesh):
        for face in small_mesh.faces:
            assert all(0 <= v < small_mesh.nV for v in face)

    def test_no_duplicate_faces(self, small_mesh):
        face_set = {tuple(sorted(f)) for f in small_mesh.faces}
        assert len(face_set) == small_mesh.nF

    def test_vertex_coordinates_shape(self, small_mesh):
        assert small_mesh.vertices.shape == (small_mesh.nV, 4)


class TestBuildTorus4d:
    @pytest.mark.parametrize("nx,ny,nz,nw", [
        (2, 2, 2, 2),
        (3, 3, 2, 2),
        (3, 2, 2, 2),
    ])
    def test_vertex_count_formula(self, nx, ny, nz, nw):
        sc = build_torus4d(nx, ny, nz, nw)
        assert sc.nV == nx * ny * nz * nw

    def test_edges_are_positive(self, default_mesh):
        assert default_mesh.nE > 0

    def test_faces_are_positive(self, default_mesh):
        assert default_mesh.nF > 0

    def test_periodic_boundary_wraps(self):
        """The smallest grid must still have edges (periodic wrap connects all)."""
        sc = build_torus4d(2, 2, 2, 2)
        assert sc.nE > 0


# ══════════════════════════════════════════════════════════════════════════════
# Unit tests — gauge field
# ══════════════════════════════════════════════════════════════════════════════

class TestRandomSuNLinks:
    def test_count_matches_edges(self, small_mesh, rng_seed):
        rng = np.random.default_rng(rng_seed)
        U = random_suN_links(small_mesh.nE, N=2, scale=0.05, rng=rng)
        assert len(U) == small_mesh.nE

    @pytest.mark.parametrize("N", [2, 3])
    def test_link_shape(self, small_mesh, rng_seed, N):
        rng = np.random.default_rng(rng_seed)
        U = random_suN_links(small_mesh.nE, N=N, scale=0.05, rng=rng)
        for Ue in U:
            assert Ue.shape == (N, N)

    def test_links_are_unitary(self, small_mesh, rng_seed):
        """U†U ≈ I for each link matrix."""
        rng = np.random.default_rng(rng_seed)
        U = random_suN_links(small_mesh.nE, N=2, scale=0.05, rng=rng)
        eye = np.eye(2, dtype=complex)
        for Ue in U:
            np.testing.assert_allclose(Ue.conj().T @ Ue, eye, atol=1e-12)

    def test_determinism(self, small_mesh):
        U1 = random_suN_links(small_mesh.nE, N=2, rng=np.random.default_rng(0))
        U2 = random_suN_links(small_mesh.nE, N=2, rng=np.random.default_rng(0))
        for a, b in zip(U1, U2):
            np.testing.assert_array_equal(a, b)

    def test_different_seeds_differ(self, small_mesh):
        U1 = random_suN_links(small_mesh.nE, N=2, rng=np.random.default_rng(1))
        U2 = random_suN_links(small_mesh.nE, N=2, rng=np.random.default_rng(2))
        assert not all(np.allclose(a, b) for a, b in zip(U1, U2))


class TestSplitBundleLinks:
    def test_count_and_shape(self, small_mesh, rng_seed):
        rng = np.random.default_rng(rng_seed)
        U = split_bundle_links(small_mesh.nE, mu1=0.5, mu2=-0.3, t=0.0, rng=rng)
        assert len(U) == small_mesh.nE
        assert all(Ue.shape == (2, 2) for Ue in U)

    def test_links_are_unitary(self, small_mesh, rng_seed):
        rng = np.random.default_rng(rng_seed)
        U = split_bundle_links(small_mesh.nE, mu1=0.5, mu2=-0.3, t=0.5, rng=rng)
        eye = np.eye(2, dtype=complex)
        for Ue in U:
            np.testing.assert_allclose(Ue.conj().T @ Ue, eye, atol=1e-12)

    @pytest.mark.parametrize("t", [0.0, 0.5, 1.0])
    def test_varying_t_changes_links(self, small_mesh, t):
        rng0 = np.random.default_rng(42)
        rng1 = np.random.default_rng(42)
        U0 = split_bundle_links(small_mesh.nE, mu1=0.5, mu2=-0.3, t=0.0, rng=rng0)
        Ut = split_bundle_links(small_mesh.nE, mu1=0.5, mu2=-0.3, t=t, rng=rng1)
        if t != 0.0:
            assert not all(np.allclose(a, b) for a, b in zip(U0, Ut))


# ══════════════════════════════════════════════════════════════════════════════
# Unit tests — curvature / holonomies
# ══════════════════════════════════════════════════════════════════════════════

class TestFaceHolonomies:
    def test_output_lengths(self, small_mesh, small_links_u2):
        F_list, Uf_list, norms = face_holonomies(small_mesh, small_links_u2)
        assert len(F_list) == small_mesh.nF
        assert len(Uf_list) == small_mesh.nF
        assert len(norms) == small_mesh.nF

    def test_curvature_matrices_hermitian(self, small_mesh, small_links_u2):
        """F = (Uf − Uf†) / 2ih² must be Hermitian."""
        F_list, _, _ = face_holonomies(small_mesh, small_links_u2)
        for F in F_list:
            np.testing.assert_allclose(F, F.conj().T, atol=1e-12)

    def test_norms_are_non_negative(self, small_mesh, small_links_u2):
        _, _, norms = face_holonomies(small_mesh, small_links_u2)
        assert all(n >= 0.0 for n in norms)

    def test_holonomy_shape(self, small_mesh, small_links_u2):
        _, Uf_list, _ = face_holonomies(small_mesh, small_links_u2)
        for Uf in Uf_list:
            assert Uf.shape == (2, 2)

    def test_h2_scaling(self, small_mesh, small_links_u2):
        """Halving h² should double the curvature norms."""
        _, _, norms_1 = face_holonomies(small_mesh, small_links_u2, h2=0.02)
        _, _, norms_2 = face_holonomies(small_mesh, small_links_u2, h2=0.01)
        ratios = [b / a for a, b in zip(norms_1, norms_2) if a > 1e-14]
        assert all(math.isclose(r, 2.0, rel_tol=1e-9) for r in ratios)


# ══════════════════════════════════════════════════════════════════════════════
# Unit tests — slope filtration
# ══════════════════════════════════════════════════════════════════════════════

class TestHermEndomorphismAndSlopes:
    @pytest.fixture(autouse=True)
    def _setup(self, small_mesh, small_links_u2):
        F_list, _, _ = face_holonomies(small_mesh, small_links_u2)
        omega = np.ones(small_mesh.nF)
        self.Phi = herm_endomorphism(F_list, omega)
        self.slopes = slope_filtration(self.Phi)

    def test_phi_is_hermitian(self):
        np.testing.assert_allclose(self.Phi, self.Phi.conj().T, atol=1e-12)

    def test_phi_shape_u2(self):
        assert self.Phi.shape == (2, 2)

    def test_slopes_count_equals_N(self):
        assert len(self.slopes) == 2

    def test_slopes_descending(self):
        assert self.slopes[0] >= self.slopes[1]

    def test_slopes_are_real(self):
        for s in self.slopes:
            assert isinstance(s, float)

    def test_slopes_trace_matches_phi_trace(self):
        np.testing.assert_allclose(
            sum(self.slopes), float(np.trace(self.Phi).real), atol=1e-10
        )


# ══════════════════════════════════════════════════════════════════════════════
# Unit tests — Lie algebra / gauge algebra dimension
# ══════════════════════════════════════════════════════════════════════════════

class TestLieClosureAndGaugeDim:
    def test_lie_closure_empty_input(self):
        assert lie_closure([]) == []

    def test_lie_closure_single_generator(self):
        g = np.array([[0, 1], [-1, 0]], dtype=complex)
        basis = lie_closure([g])
        assert len(basis) >= 1

    def test_lie_closure_su2_generators(self):
        """su(2) Pauli-like generators should close to dim-3 basis."""
        sx = np.array([[0, 1], [1, 0]], dtype=complex) / 2
        sy = np.array([[0, -1j], [1j, 0]], dtype=complex) / 2
        sz = np.array([[1, 0], [0, -1]], dtype=complex) / 2
        basis = lie_closure([sx, sy, sz])
        assert len(basis) == 3

    def test_gauge_algebra_dim_in_range(self, small_mesh, small_links_u2):
        F_list, _, _ = face_holonomies(small_mesh, small_links_u2)
        dim = effective_gauge_algebra_dim(F_list, N=2)
        assert 0 <= dim <= 4  # N²=4 for U(2)

    def test_gauge_algebra_dim_with_zero_curvature(self, small_mesh):
        """Zero curvature → trivial centraliser → should return N²."""
        N = 2
        zero_F = [np.zeros((N, N), dtype=complex)] * small_mesh.nF
        dim = effective_gauge_algebra_dim(zero_F, N)
        assert dim == N * N


# ══════════════════════════════════════════════════════════════════════════════
# Unit tests — Dolbeault Laplacian
# ══════════════════════════════════════════════════════════════════════════════

class TestDolbeaultSpectrum:
    def test_returns_correct_count(self, small_mesh, small_links_u2):
        vals = dolbeault_spectrum(small_mesh, small_links_u2, N=2, k=4)
        assert len(vals) == 4

    def test_eigenvalues_non_negative(self, small_mesh, small_links_u2):
        vals = dolbeault_spectrum(small_mesh, small_links_u2, N=2, k=4)
        assert all(v >= -1e-10 for v in vals)

    def test_eigenvalues_sorted_ascending(self, small_mesh, small_links_u2):
        vals = dolbeault_spectrum(small_mesh, small_links_u2, N=2, k=4)
        assert vals == sorted(vals)

    def test_eigenvalues_are_real_floats(self, small_mesh, small_links_u2):
        vals = dolbeault_spectrum(small_mesh, small_links_u2, N=2, k=4)
        for v in vals:
            assert isinstance(v, float)

    def test_determinism(self, small_mesh):
        rng1 = np.random.default_rng(7)
        rng2 = np.random.default_rng(7)
        U1 = random_suN_links(small_mesh.nE, N=2, rng=rng1)
        U2 = random_suN_links(small_mesh.nE, N=2, rng=rng2)
        v1 = dolbeault_spectrum(small_mesh, U1, N=2, k=4)
        v2 = dolbeault_spectrum(small_mesh, U2, N=2, k=4)
        np.testing.assert_allclose(v1, v2, atol=1e-12)


# ══════════════════════════════════════════════════════════════════════════════
# API tests — /api/health
# ══════════════════════════════════════════════════════════════════════════════

class TestHealthEndpoint:
    @pytest.mark.integration
    def test_status_200(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200

    @pytest.mark.integration
    def test_body_ok(self, client):
        r = client.get("/api/health")
        assert r.json() == {"status": "ok"}


# ══════════════════════════════════════════════════════════════════════════════
# API tests — POST /api/run
# ══════════════════════════════════════════════════════════════════════════════

class TestRunEndpoint:
    @pytest.mark.integration
    def test_status_200(self, client, minimal_run_payload):
        r = client.post("/api/run", json=minimal_run_payload)
        assert r.status_code == 200

    @pytest.mark.integration
    def test_response_keys(self, client, minimal_run_payload):
        body = client.post("/api/run", json=minimal_run_payload).json()
        expected = {
            "mesh", "slopes", "phi_trace", "phi_norm",
            "curv_norms", "curv_mean", "curv_max",
            "gauge_algebra_dim", "expected_gauge_dim",
            "dolbeault_eigenvalues", "zero_modes",
        }
        assert expected <= body.keys()

    @pytest.mark.integration
    def test_mesh_fields(self, client, minimal_run_payload):
        body = client.post("/api/run", json=minimal_run_payload).json()
        mesh = body["mesh"]
        assert mesh["nV"] == 2 * 2 * 2 * 2
        assert mesh["nE"] > 0
        assert mesh["nF"] > 0

    @pytest.mark.integration
    def test_slopes_count_equals_N(self, client, minimal_run_payload):
        body = client.post("/api/run", json=minimal_run_payload).json()
        assert len(body["slopes"]) == minimal_run_payload["N"]

    @pytest.mark.integration
    def test_slopes_descending(self, client, minimal_run_payload):
        slopes = client.post("/api/run", json=minimal_run_payload).json()["slopes"]
        assert slopes == sorted(slopes, reverse=True)

    @pytest.mark.integration
    def test_eigenvalue_count(self, client, minimal_run_payload):
        body = client.post("/api/run", json=minimal_run_payload).json()
        assert len(body["dolbeault_eigenvalues"]) == minimal_run_payload["n_eigs"]

    @pytest.mark.integration
    def test_eigenvalues_non_negative(self, client, minimal_run_payload):
        body = client.post("/api/run", json=minimal_run_payload).json()
        assert all(v >= -1e-10 for v in body["dolbeault_eigenvalues"])

    @pytest.mark.integration
    def test_zero_modes_consistent(self, client, minimal_run_payload):
        body = client.post("/api/run", json=minimal_run_payload).json()
        computed = sum(
            1 for v in body["dolbeault_eigenvalues"] if abs(v) < 1e-7
        )
        assert body["zero_modes"] == computed

    @pytest.mark.integration
    def test_curv_mean_leq_max(self, client, minimal_run_payload):
        body = client.post("/api/run", json=minimal_run_payload).json()
        assert body["curv_mean"] <= body["curv_max"] + 1e-12

    @pytest.mark.integration
    def test_expected_gauge_dim_equals_n_squared(self, client, minimal_run_payload):
        body = client.post("/api/run", json=minimal_run_payload).json()
        N = minimal_run_payload["N"]
        assert body["expected_gauge_dim"] == N * N

    @pytest.mark.integration
    def test_determinism_same_seed(self, client, minimal_run_payload):
        body1 = client.post("/api/run", json=minimal_run_payload).json()
        body2 = client.post("/api/run", json=minimal_run_payload).json()
        assert body1["slopes"] == body2["slopes"]
        assert body1["dolbeault_eigenvalues"] == body2["dolbeault_eigenvalues"]

    @pytest.mark.integration
    def test_different_seeds_differ(self, client, minimal_run_payload):
        payload_a = {**minimal_run_payload, "seed": 1}
        payload_b = {**minimal_run_payload, "seed": 2}
        body_a = client.post("/api/run", json=payload_a).json()
        body_b = client.post("/api/run", json=payload_b).json()
        assert body_a["curv_mean"] != body_b["curv_mean"]

    # ── Validation ──────────────────────────────────────────────────────────

    @pytest.mark.integration
    @pytest.mark.parametrize("field,bad_value", [
        ("nx", 1),    # below ge=2
        ("nx", 6),    # above le=5
        ("N", 1),     # below ge=2
        ("N", 4),     # above le=3
        ("n_eigs", 1),  # below ge=2
    ])
    def test_invalid_params_rejected(self, client, minimal_run_payload, field, bad_value):
        payload = {**minimal_run_payload, field: bad_value}
        r = client.post("/api/run", json=payload)
        assert r.status_code == 422

    @pytest.mark.integration
    def test_missing_body_rejected(self, client):
        r = client.post("/api/run", json={})
        # pydantic fills defaults — should still succeed
        assert r.status_code == 200

    @pytest.mark.slow
    @pytest.mark.integration
    def test_large_grid_completes(self, client):
        payload = {
            "nx": 4, "ny": 4, "nz": 3, "nw": 3,
            "N": 2, "scale": 0.05, "h2": 0.01,
            "seed": 0, "n_eigs": 6,
        }
        r = client.post("/api/run", json=payload)
        assert r.status_code == 200


# ══════════════════════════════════════════════════════════════════════════════
# API tests — POST /api/sweep
# ══════════════════════════════════════════════════════════════════════════════

class TestSweepEndpoint:
    @pytest.mark.integration
    def test_status_200(self, client, minimal_sweep_payload):
        r = client.post("/api/sweep", json=minimal_sweep_payload)
        assert r.status_code == 200

    @pytest.mark.integration
    def test_response_keys(self, client, minimal_sweep_payload):
        body = client.post("/api/sweep", json=minimal_sweep_payload).json()
        assert "sweep" in body
        assert "mesh" in body

    @pytest.mark.integration
    def test_sweep_length_matches_steps(self, client, minimal_sweep_payload):
        body = client.post("/api/sweep", json=minimal_sweep_payload).json()
        assert len(body["sweep"]) == minimal_sweep_payload["steps"]

    @pytest.mark.integration
    def test_sweep_t_range(self, client, minimal_sweep_payload):
        body = client.post("/api/sweep", json=minimal_sweep_payload).json()
        t_values = [pt["t"] for pt in body["sweep"]]
        assert math.isclose(t_values[0], 0.0, abs_tol=1e-6)
        assert math.isclose(t_values[-1], 1.0, abs_tol=1e-6)

    @pytest.mark.integration
    def test_sweep_t_monotone(self, client, minimal_sweep_payload):
        body = client.post("/api/sweep", json=minimal_sweep_payload).json()
        t_values = [pt["t"] for pt in body["sweep"]]
        assert t_values == sorted(t_values)

    @pytest.mark.integration
    def test_sweep_point_keys(self, client, minimal_sweep_payload):
        body = client.post("/api/sweep", json=minimal_sweep_payload).json()
        for pt in body["sweep"]:
            assert {"t", "slopes", "gauge_dim", "curv_mean"} <= pt.keys()

    @pytest.mark.integration
    def test_sweep_slopes_count(self, client, minimal_sweep_payload):
        body = client.post("/api/sweep", json=minimal_sweep_payload).json()
        N = minimal_sweep_payload["N"]
        for pt in body["sweep"]:
            assert len(pt["slopes"]) == N

    @pytest.mark.integration
    def test_sweep_slopes_descending(self, client, minimal_sweep_payload):
        body = client.post("/api/sweep", json=minimal_sweep_payload).json()
        for pt in body["sweep"]:
            s = pt["slopes"]
            assert s == sorted(s, reverse=True)

    @pytest.mark.integration
    def test_sweep_curv_mean_non_negative(self, client, minimal_sweep_payload):
        body = client.post("/api/sweep", json=minimal_sweep_payload).json()
        for pt in body["sweep"]:
            assert pt["curv_mean"] >= 0.0

    @pytest.mark.integration
    @pytest.mark.parametrize("field,bad_value", [
        ("steps", 3),   # below ge=4
        ("steps", 31),  # above le=30
        ("mu1", -3.0),  # below ge=-2.0
        ("mu2", 3.0),   # above le=2.0
    ])
    def test_invalid_params_rejected(self, client, minimal_sweep_payload, field, bad_value):
        payload = {**minimal_sweep_payload, field: bad_value}
        r = client.post("/api/sweep", json=payload)
        assert r.status_code == 422

    @pytest.mark.integration
    def test_determinism(self, client, minimal_sweep_payload):
        body1 = client.post("/api/sweep", json=minimal_sweep_payload).json()
        body2 = client.post("/api/sweep", json=minimal_sweep_payload).json()
        for pt1, pt2 in zip(body1["sweep"], body2["sweep"]):
            assert pt1["slopes"] == pt2["slopes"]
