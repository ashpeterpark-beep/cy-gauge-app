# Discrete Calabi–Yau Gauge Functor — Web App

Full-stack web interface for the CY gauge functor pipeline.
**FastAPI** backend runs the real numpy/scipy pipeline.
**React + Vite** frontend visualizes results interactively.

---

## Architecture

```
cy-gauge-app/
├── backend/
│   ├── main.py         
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx     
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── docker-compose.yml
```

---

## Quick Start (Docker — recommended)

```bash
cd cy-gauge-app
docker-compose up --build
```

- Frontend → http://localhost:5173
- Backend API → http://localhost:8000
- API docs → http://localhost:8000/docs

---

## Manual Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Liveness check |
| POST | `/api/run` | Full simulation (mesh + gauge + Laplacian) |
| POST | `/api/sweep` | Wall-crossing sweep over mixing t |

### POST /api/run — parameters
| Field | Default | Range | Description |
|-------|---------|-------|-------------|
| `nx,ny,nz,nw` | 3,3,2,2 | 2–5 | 4-torus grid dimensions |
| `N` | 2 | 2–3 | U(N) gauge group rank |
| `scale` | 0.05 | 0.001–0.5 | Link scale ε |
| `h2` | 0.01 | 0.001–0.2 | Lattice spacing h² |
| `seed` | 42 | 0–9999 | RNG seed |
| `n_eigs` | 10 | 2–30 | Dolbeault Laplacian eigenvalues |

### POST /api/sweep — parameters
Same mesh/gauge params plus:
| Field | Default | Description |
|-------|---------|-------------|
| `mu1` | 0.5 | Split bundle phase μ₁ |
| `mu2` | -0.3 | Split bundle phase μ₂ |
| `steps` | 12 | Number of t ∈ [0,1] steps |

---

## What each tab shows

- **Curvature** — heat map of per-face ‖F_f‖ from real `face_holonomies()`
- **Wall-Crossing** — slope filtration λ₁,λ₂ vs mixing t (full sweep)
- **Spectrum** — Dolbeault Laplacian eigenvalues via sparse `eigsh` + shift-invert
- **Data** — raw numerics: Φ trace/norm, gauge algebra dimension, zero modes

---

## Deploy to the cloud

### Backend → Railway / Render
Push `backend/` to a GitHub repo, connect to Railway or Render,
set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend → Vercel / Netlify
```bash
cd frontend
npm run build          # outputs dist/
```
Upload `dist/` to Vercel. Set env var:
```
VITE_API_URL=https://your-backend.railway.app
```

### Free option: Hugging Face Spaces
Use a **Docker** Space, paste the `docker-compose.yml` approach,
or deploy backend as a Gradio/FastAPI Space and host frontend on Vercel.
