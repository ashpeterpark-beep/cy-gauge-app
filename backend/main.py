"""
Discrete Calabi–Yau Gauge Functor – FastAPI Backend
====================================================
Exposes the full pipeline as REST endpoints:
  POST /api/run        – full simulation (mesh + gauge + Laplacian)
  POST /api/sweep      – wall-crossing sweep over mixing parameter t
  GET  /api/health     – liveness check
"""

import warnings

import numpy as np
from fastapi import Depends, FastAPI, HTTPException, Request
from scipy.linalg import eigh, expm
from scipy.sparse import coo_matrix
from scipy.sparse import eye as speye
from scipy.sparse.linalg import LinearOperator, eigsh, splu

from auth import require_auth
from middleware import limiter, register_middleware
from schemas import HealthResponse, RunParams, RunResponse, SweepParams, SweepResponse

warnings.filterwarnings("ignore")

app = FastAPI(title="CY Gauge Functor API", version="1.0.0")

# Replaces the old hardcoded CORSMiddleware block —
# reads CORS_ORIGINS, rate limiter, request logging, trusted hosts from env
register_middleware(app)


# ─── SimplicialComplex ─────────────────────────────────────────────────────────

class SimplicialComplex:
    def __init__(self, vertices, edges, faces):
        self.vertices = np.asarray(vertices, dtype=float)
        self.edges = edges
        self.faces = faces
        self.nV = len(vertices)
        self.nE = len(edges)
        self.nF = len(faces)
        self.edge_index = {tuple(sorted(e)): i for i, e in enumerate(edges)}


def build_torus4d(nx=3, ny=3, nz=2, nw=2):
    xs = np.linspace(0, 2 * np.pi, nx, endpoint=False)
    ys = np.linspace(0, 2 * np.pi, ny, endpoint=False)
    zs = np.linspace(0, 2 * np.pi, nz, endpoint=False)
    ws = np.linspace(0, 2 * np.pi, nw, endpoint=False)
    vertices = [[x, y, z, w] for x in xs for y in ys for z in zs for w in ws]
    V = len(vertices)
    steps = [2 * np.pi / n for n in [nx, ny, nz, nw]]
    edges = set()
    for i in range(V):
        for j in range(i + 1, V):
            diff = [abs(vertices[i][d] - vertices[j][d]) for d in range(4)]
            diff_wrap = [min(d, 2 * np.pi - d) for d in diff]
            for d in range(4):
                if abs(diff_wrap[d] - steps[d]) < 1e-6 and all(
                    diff_wrap[k] < 1e-6 for k in range(4) if k != d
                ):
                    edges.add((i, j))
                    break
    edges = list(edges)
    adj = {i: set() for i in range(V)}
    for i, j in edges:
        adj[i].add(j)
        adj[j].add(i)
    faces = set()
    for i in range(V):
        neigh = list(adj[i])
        for a in range(len(neigh)):
            for b in range(a + 1, len(neigh)):
                j, k = neigh[a], neigh[b]
                if k in adj[j]:
                    faces.add(tuple(sorted((i, j, k))))
    return SimplicialComplex(vertices, edges, list(faces))


# ─── Gauge field ───────────────────────────────────────────────────────────────

def random_suN_links(nE, N=2, scale=0.05, rng=None):
    if rng is None:
        rng = np.random.default_rng(42)
    U = []
    for _ in range(nE):
        H = rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))
        H = (H + H.conj().T) / 2
        A = 1j * scale * H
        U.append(expm(A))
    return U


def split_bundle_links(nE, mu1, mu2, t=0.0, scale=0.05, rng=None):
    if rng is None:
        rng = np.random.default_rng(42)
    N = 2
    U = []
    for _ in range(nE):
        phi1 = mu1 * rng.standard_normal()
        phi2 = mu2 * rng.standard_normal()
        A = (
            np.diag([phi1, phi2]).astype(complex)
            + t * np.array([[0, 1], [1, 0]], dtype=complex)
        )
        U.append(expm(1j * scale * A))
    return U


# ─── Curvature ─────────────────────────────────────────────────────────────────

def face_holonomies(sc, U_edges, h2=0.01):
    F_list, Uf_list, norms = [], [], []
    for face in sc.faces:
        i, j, k = face
        e1 = sc.edge_index[tuple(sorted((i, j)))]
        e2 = sc.edge_index[tuple(sorted((j, k)))]
        e3 = sc.edge_index[tuple(sorted((k, i)))]
        Uf = U_edges[e1] @ U_edges[e2] @ U_edges[e3]
        Uf_list.append(Uf)
        F = (Uf - Uf.conj().T) / (2j * h2)
        F_list.append(F)
        norms.append(float(np.linalg.norm(F)))
    return F_list, Uf_list, norms


# ─── Hermitian endomorphism + slope filtration ─────────────────────────────────

def herm_endomorphism(F_faces, omega_faces):
    N = F_faces[0].shape[0]
    Phi = np.zeros((N, N), dtype=complex)
    for F, w in zip(F_faces, omega_faces):
        Phi += w * F
    return (Phi + Phi.conj().T) / 2


def slope_filtration(Phi):
    eigvals, _ = eigh(Phi)
    return sorted(eigvals.tolist(), reverse=True)


# ─── Lie algebra + centraliser ─────────────────────────────────────────────────

def lie_closure(generators, tol=1e-10):
    basis = []

    def normalize(x):
        x = (x - x.conj().T) / 2
        n = np.linalg.norm(x)
        return x / n if n > tol else None

    for g in generators:
        g_n = normalize(g)
        if g_n is not None and not any(np.linalg.norm(g_n - b) < tol for b in basis):
            basis.append(g_n)
    changed = True
    while changed:
        changed = False
        new = []
        for a in basis:
            for b in basis:
                c = a @ b - b @ a
                c_n = normalize(c)
                if c_n is not None and not any(
                    np.linalg.norm(c_n - x) < tol for x in basis + new
                ):
                    new.append(c_n)
        if new:
            basis.extend(new)
            changed = True
    return basis


def effective_gauge_algebra_dim(F_faces, N):
    gens = [F for F in F_faces if np.linalg.norm(F) > 1e-12]
    if not gens:
        return N * N
    lie_basis = lie_closure(gens)
    if not lie_basis:
        return N * N
    dim = N * N
    M = []
    for g in lie_basis:
        G = np.kron(np.eye(N), g) - np.kron(g.T, np.eye(N))
        M.append(G)
    M = np.vstack(M)
    null_dim = dim - np.linalg.matrix_rank(M)
    return int(null_dim)


# ─── Dolbeault Laplacian ───────────────────────────────────────────────────────

def build_dbar_sparse(sc, U_edges, N=2):
    nV, nE = sc.nV, sc.nE
    rows, cols, data = [], [], []
    weight = 0.5
    for e_idx, (v, w) in enumerate(sc.edges):
        Ue = U_edges[e_idx]
        for i in range(N):
            for j in range(N):
                rows.append(e_idx * N + i)
                cols.append(v * N + j)
                data.append(-weight * (1.0 if i == j else 0.0))
                rows.append(e_idx * N + i)
                cols.append(w * N + j)
                data.append(weight * Ue[i, j])
    Dbar = coo_matrix(
        (data, (rows, cols)), shape=(nE * N, nV * N), dtype=complex
    ).tocsr()
    return Dbar


def dolbeault_spectrum(sc, U_edges, N=2, k=10):
    Dbar = build_dbar_sparse(sc, U_edges, N)
    Lap = (Dbar.conj().T @ Dbar).tocsc()
    n = Lap.shape[0]
    k = min(k, n - 2)
    try:
        sigma = 1e-8
        A = Lap - sigma * speye(n, format="csc")
        lu = splu(A)
        op = LinearOperator(
            (n, n), matvec=lambda x: lu.solve(x), dtype=complex
        )
        vals, _ = eigsh(op, k=k, which="LM")
        eigvals = sorted((sigma + 1.0 / v).real for v in vals)
    except Exception:
        vals, _ = eigh(Lap.toarray())
        eigvals = sorted(vals[:k].real.tolist())
    return eigvals


# ─── API endpoints ─────────────────────────────────────────────────────────────

@app.get("/api/health", response_model=HealthResponse)
def health():
    """Liveness check — always public, no auth required."""
    return HealthResponse(status="ok", version="1.0.0")


@app.post("/api/run", response_model=RunResponse, dependencies=[Depends(require_auth)])
@limiter.limit("10/minute")
def run_simulation(request: Request, p: RunParams):
    """
    Full simulation: mesh build → gauge links → curvature → slope filtration
    → Dolbeault Laplacian spectrum.
    Requires X-API-Key header when AUTH_ENABLED=true.
    Rate limited to 10 requests/minute per IP.
    """
    try:
        rng = np.random.default_rng(p.seed)
        sc = build_torus4d(p.nx, p.ny, p.nz, p.nw)
        omega = np.ones(sc.nF)
        U_edges = random_suN_links(sc.nE, N=p.N, scale=p.scale, rng=rng)
        F_faces, _, curv_norms = face_holonomies(sc, U_edges, h2=p.h2)
        Phi = herm_endomorphism(F_faces, omega)
        slopes = slope_filtration(Phi)
        gauge_dim = effective_gauge_algebra_dim(F_faces, p.N)
        eigvals = dolbeault_spectrum(sc, U_edges, N=p.N, k=p.n_eigs)
        zero_modes = sum(1 for v in eigvals if abs(v) < 1e-7)

        return RunResponse(
            mesh={"nV": sc.nV, "nE": sc.nE, "nF": sc.nF},
            slopes=slopes,
            phi_trace=float(np.trace(Phi).real),
            phi_norm=float(np.linalg.norm(Phi)),
            curv_norms=curv_norms,
            curv_mean=float(np.mean(curv_norms)),
            curv_max=float(np.max(curv_norms)),
            gauge_algebra_dim=gauge_dim,
            expected_gauge_dim=p.N * p.N,
            dolbeault_eigenvalues=eigvals,
            zero_modes=zero_modes,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sweep", response_model=SweepResponse, dependencies=[Depends(require_auth)])
@limiter.limit("5/minute")
def wall_crossing_sweep(request: Request, p: SweepParams):
    """
    Wall-crossing sweep: runs the gauge pipeline at each step of mixing
    parameter t ∈ [0, 1] and returns slope filtration per step.
    Requires X-API-Key header when AUTH_ENABLED=true.
    Rate limited to 5 requests/minute per IP (heavier compute than /run).
    """
    try:
        sc = build_torus4d(p.nx, p.ny, p.nz, p.nw)
        omega = np.ones(sc.nF)
        results = []

        for i in range(p.steps):
            t = i / (p.steps - 1)
            rng = np.random.default_rng(p.seed)
            U = split_bundle_links(sc.nE, p.mu1, p.mu2, t=t, scale=p.scale, rng=rng)
            F_faces, _, curv_norms = face_holonomies(sc, U, h2=p.h2)
            Phi = herm_endomorphism(F_faces, omega)
            slopes = slope_filtration(Phi)
            gauge_dim = effective_gauge_algebra_dim(F_faces, p.N)
            results.append({
                "t": round(t, 4),
                "slopes": slopes,
                "gauge_dim": gauge_dim,
                "curv_mean": float(np.mean(curv_norms)),
            })

        return SweepResponse(
            sweep=results,
            mesh={"nV": sc.nV, "nE": sc.nE, "nF": sc.nF},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
