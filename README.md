<div align="center">

# Discrete Calabi–Yau Gauge Functor Dashboard

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![SciPy](https://img.shields.io/badge/SciPy-NumPy-8CAAE6?logo=scipy&logoColor=white)](https://scipy.org)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF?logo=vite&logoColor=white)](https://vitejs.dev)

**Full-stack interactive platform for lattice gauge theory on a discrete Calabi–Yau 4-torus.**

*FastAPI backend · React + Vite frontend · Real NumPy/SciPy numerical pipeline*

</div>

---

## Figure 1 — T⁴ Lattice Geometry (3D Projection)

The app simulates gauge theory on a **discrete 4-torus T⁴**. Below is a 3D projection of the lattice mesh — each point is a vertex, coloured by curvature norm ‖F_f‖. Edges connect nearest neighbours under the periodic boundary conditions.

![T⁴ Lattice Mesh — 3D projection of the discrete Calabi–Yau geometry](fig1_torus3d.png)

> The 4D manifold is projected into R³ via a Hopf-like fibration. Vertex colour maps to the local U(N) gauge field curvature.

---

## Figure 2 — Face Curvature Heatmap (Tab ① Curvature)

The first dashboard tab renders a live heatmap of **per-face curvature norms ‖F_f‖**, computed from real `face_holonomies()` in the FastAPI backend. Each cell is one triangular face of the simplicial mesh.

![Face curvature heatmap showing per-face ‖F_f‖ values](fig2_heatmap.png)

> **Cold (purple/blue)** = low curvature · **Hot (yellow/white)** = high curvature.  
> Cell labels show exact values. Updated live on every parameter change.

---

## Figure 3 — Wall-Crossing Sweep (Tab ② Wall-Crossing)

As the bundle-mixing parameter **t** sweeps from 0 → 1, the slope eigenvalues **λ₁(t)** and **λ₂(t)** trace trajectories. When λ₁ crosses zero, a **Harder–Narasimhan wall** is detected — the bundle changes stability type.

![Wall-crossing sweep showing slope filtration λ₁(t) and λ₂(t)](fig3_wallcrossing.png)

> **Teal line** = λ₁(t) · **Orange line** = λ₂(t) · **Dashed yellow** = semistability wall (λ = 0) · **Purple dotted** = detected HN wall crossing.

---

## Figure 4 — Dolbeault Laplacian Spectrum (Tab ③ Spectrum)

The FEEC Dolbeault operator **∂̄** is assembled as a sparse matrix and its Laplacian **Δ = ∂̄†∂̄** diagonalised via `scipy.sparse.linalg.eigsh` with shift-invert. Eigenvalues near zero (< 1e-7) are counted as **zero modes** — harmonic (0,1)-forms.

![Dolbeault Laplacian eigenvalue spectrum with zero mode highlighted in yellow](fig4_spectrum.png)

> **Yellow bar** = zero mode (harmonic form) · **Teal–blue gradient** = higher eigenvalues.  
> Number of zero modes equals the dimension of the kernel of Δ.

---

## Figure 5 — Numerical Pipeline Architecture

Every computation runs server-side in Python. The diagram below maps the exact call graph in `main.py`.

![Numerical pipeline: T⁴ mesh → SU(N) links → holonomies → endomorphism → slopes + spectrum](fig5_pipeline.png)

---

## Figure 6 — Gauge Bundle Slope Surfaces (3D)

The **Hermitian endomorphism Φ = Σ ω_f · F_f** evaluated over T⁴ produces two slope surfaces corresponding to eigenvalues λ₁ and λ₂. The geometry of these surfaces encodes the stability of the gauge bundle.

![3D slope surfaces of the Hermitian endomorphism Φ over the torus](fig6_slopes3d.png)

> Left: **λ₁** surface at t = 0 (initial bundle, teal). Right: **λ₂** surface at t = 1 (mixed bundle, orange).

---

## Architecture

```
cy-gauge-app/
├── main.py            ← FastAPI backend — full scipy/numpy pipeline
├── requirements.txt   ← Python dependencies
├── Dockerfile
│
├── App.jsx            ← React root component (all 4 tabs + canvas rendering)
├── main.jsx           ← Vite entry point
├── index.html
├── package.json
├── vite.config.js     ← proxies /api/* → :8000
└── docker-compose.yml ← orchestrates both services
```

```
Browser  (React + Vite,  port 5173)
    │
    │  POST /api/run    →  mesh + gauge + holonomies + slopes + spectrum
    │  POST /api/sweep  →  wall-crossing sweep λ(t) over N steps
    │  GET  /api/health →  liveness check
    ▼
FastAPI backend  (port 8000)
    ├── build_torus4d()              builds T⁴ simplicial complex
    ├── random_suN_links()           SU(N) links via matrix exp
    ├── face_holonomies()            curvature F_f per face
    ├── herm_endomorphism()          Φ = Σ ω_f F_f
    ├── slope_filtration()           eigh → λ₁, λ₂
    ├── effective_gauge_algebra_dim() Lie closure dimension
    └── dolbeault_spectrum()         sparse eigsh shift-invert
```

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite 5 |
| Visualisation | Raw HTML5 `<canvas>` (no charting lib) |
| Backend | FastAPI 0.115 |
| Linear algebra | NumPy, SciPy |
| Sparse eigensolver | `eigsh` + `splu` shift-invert |
| Matrix exponential | `scipy.linalg.expm` |
| Containers | Docker + docker-compose |

---

## Dashboard Tabs

| Tab | Visualisation | Backend call |
|-----|--------------|-------------|
| **① Curvature** | Heatmap of ‖F_f‖ per face | `POST /api/run` |
| **② Wall-Crossing** | λ₁(t), λ₂(t) line chart | `POST /api/sweep` |
| **③ Spectrum** | Dolbeault eigenvalue bar chart | `POST /api/run` |
| **④ Data** | Raw numerics table | `POST /api/run` |

---

## Quick Start

### Docker (recommended)

```bash
git clone https://github.com/ashpeterpark-beep/cy-gauge-app.git
cd cy-gauge-app
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger docs | http://localhost:8000/docs |

### Manual setup

```bash
# Backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (separate terminal)
npm install && npm run dev
```

---

## API Reference

### `GET /api/health`
```json
{ "status": "ok" }
```

### `POST /api/run` — Full simulation

| Field | Default | Range | Description |
|-------|---------|-------|-------------|
| `nx`, `ny` | 3 | 2–5 | Grid points along x / y |
| `nz`, `nw` | 2 | 2–4 | Grid points along z / w |
| `N` | 2 | 2–3 | U(N) gauge group rank |
| `scale` | 0.05 | 0.001–0.5 | Link scale ε |
| `h2` | 0.01 | 0.001–0.2 | Lattice spacing h² |
| `seed` | 42 | 0–9999 | RNG seed |
| `n_eigs` | 10 | 2–30 | Dolbeault eigenvalues to compute |

### `POST /api/sweep` — Wall-crossing

Same mesh/gauge params, plus:

| Field | Default | Description |
|-------|---------|-------------|
| `mu1` | 0.5 | Split-bundle phase μ₁ |
| `mu2` | -0.3 | Split-bundle phase μ₂ |
| `steps` | 12 | Number of t ∈ [0,1] steps |

---

## Deployment

**Backend → Railway / Render**
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Frontend → Vercel / Netlify**
```bash
npm run build   # produces dist/
# Set environment variable:
# VITE_API_URL=https://your-backend.railway.app
```

**Free option — Hugging Face Spaces:** use a Docker Space with the existing `docker-compose.yml`.

---

## Mathematical Symbols

| Symbol | Meaning |
|--------|---------|
| T⁴ | Discrete 4-torus (Calabi–Yau approximation) |
| U(N) | Unitary gauge group (N = 2 or 3) |
| U_e | SU(N) link variable on edge e |
| F_f | Curvature 2-form on face f |
| Φ | Hermitian endomorphism (gauge functor image) |
| λ₁, λ₂ | Harder–Narasimhan slope eigenvalues |
| ∂̄ | Dolbeault operator (FEEC discretisation) |
| Δ | Dolbeault Laplacian Δ = ∂̄†∂̄ |
| h² | Lattice spacing squared |
| ε | Link scale parameter |
| t | Bundle-mixing parameter (wall-crossing) |

---

## License

MIT © Gaius Lumen — see [LICENSE](./LICENSE..%20md)

[![Twitter](https://img.shields.io/badge/@GaiusLumen-1DA1F2?logo=twitter&logoColor=white)](https://twitter.com/GaiusLumen)
[![Email](https://img.shields.io/badge/gaiuslumen@gmail.com-D14836?logo=gmail&logoColor=white)](mailto:gaiuslumen@gmail.com)
