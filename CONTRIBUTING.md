# Contributing to `cy‑gauge‑app`

First off, thank you for your interest in contributing to the **Discrete Calabi–Yau Gauge Functor Dashboard**!   
Whether you are a physicist, a numerical analyst, or a full‑stack developer, your help is very welcome.

The project is open‑source under the MIT licence. Before you start, please take a moment to read this short guide. It explains how to report issues, propose features, set up a development environment, and submit code changes.

## 1. Code of conduct

We expect all participants to be respectful and constructive.  
Be kind, help others, and assume good intentions. Offensive or inappropriate behaviour will not be tolerated.

## 2. Ways to contribute

You do not have to write code to help. Other valuable contributions include:

- Reporting a bug or a numerical instability.
- Suggesting a new feature (e.g. a new gauge group, a different lattice geometry, or an additional export format).
- Improving the documentation, examples, or inline comments.
- Reviewing pull requests and helping to test new changes.

## 3. Reporting issues / requesting features

Use the [GitHub issue tracker](https://github.com/ashpeterpark-beep/cy-gauge-app/issues).

- **Bug reports** – please include:
  - The exact steps to reproduce the problem.
  - The expected behaviour and what you actually observed.
  - The output of the backend logs (if relevant).
  - Your environment: Python version, npm version, browser, etc.

- **Feature requests** – please describe:
  - The problem you are trying to solve.
  - A concrete proposal (screenshots or API examples are very helpful).
  - Whether you are willing to work on it yourself.

## 4. Setting up a development environment

The project uses a **FastAPI backend** and a **React + Vite frontend**.  
You can run everything manually or use Docker.

### 4.1 Clone the repository

```bash
git clone https://github.com/ashpeterpark-beep/cy-gauge-app.git
cd cy-gauge-app
```
###4.2 Backend (Python)

```bash
cd backend
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Dependencies are pinned: fastapi==0.111.0, uvicorn[standard]==0.29.0, numpy==1.26.4, scipy==1.13.0, pydantic==2.7.1.

4.3 Frontend (React + Vite)

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:5173 and the API at http://localhost:8000.

Note: If you see CORS errors, make sure the frontend proxy or the backend CORS middleware is correctly configured. The backend already includes CORSMiddleware with allow_origins=["*"] for development.

4.4 Using Docker (recommended for testing)

```bash
docker-compose up --build
```

Both services will start in containers, and logs from both will be shown in the terminal.

5. Making changes – step by step

1. Find or create an issue – Let others know you are working on something.
2. Fork the repository and create a new branch from main.
   Use a descriptive name, e.g. fix/wallcrossing-divergence or feat/faster-eigensolver.
3. Write your code – follow the existing style.
4. Test your changes – at a minimum, run the existing examples and check that the dashboard still works.
5. Run the linter / formatter (if you have them installed):
   · For Python: black . and isort .
   · For JavaScript/JSX: npx prettier --write .
6. Commit – use a clear commit message.
7. Push to your fork and open a pull request against the main branch.

6. Coding guidelines

6.1 Python

· Follow PEP 8.
· Use type hints for function arguments and return values (the backend already uses Pydantic models).
· Keep numerical code readable – avoid overly compact expressions.

6.2 JavaScript / React

· Use functional components and React hooks (the existing code uses useState, useEffect, etc.).
· Keep canvas‑drawing logic inside helper functions (see drawHeatmap in App.jsx).
· Avoid inline styles for complex components; use CSS modules or a separate .css file.

6.3 General

· Do not commit large binary files (images, datasets) unless strictly necessary.
· Do not commit sensitive information (API keys, passwords, etc.).
· Write comments when the logic is not immediately obvious (especially for the FEEC / numerical linear algebra parts).

7. Testing

 Running tests
make test       
make test-cov   
Tests are located in tests/ and use pytest + httpx (via FastAPI's TestClient).

we encourage you to add tests if you are extending the core numerical routines.

· A tests/ directory is ready for future test modules (e.g. tests/test_curvature.py, tests/test_wallcrossing.py).
· If you add a new feature, please include a minimal example or a short script that verifies the result.


8. Documentation

· Update the README.md if you change the setup instructions or the API.
· If you add a new dashboard tab, describe it in the Dashboard Tabs section of the README.md.
· For larger changes, consider adding a short explanation in the Docs/ folder (e.g. Docs/new-algorithm.md).

9. Pull request checklist

Before submitting a pull request, please confirm:

· The code follows the existing style and passes the linter (if run).
· The change works both manually and with Docker.
· You have tested the relevant dashboard tabs (curvature, wall‑crossing, spectrum).
· You have updated the documentation (if needed).
· The commit history is clean (no merge commits, no unrelated changes).

10. Questions?

Open a GitHub issue with the label question or reach out via the discussion board. We will try to answer as quickly as possible.


12. Pull request checklist

[ ] make format && make lint passes with no errors
[ ] make test passes with no failures
[ ] New public functions/classes have docstrings
[ ] PR description explains why, not just what

13. Commit message convention
<type>(<scope>): <short summary>

Types: feat | fix | refactor | test | docs | chore
Examples:
feat(api): add /api/sweep endpoint for wall-crossing
fix(mesh): correct periodic boundary wrap in build_torus4d
test(laplacian): add eigenvalue non-negativity assertion
Reporting issues

14. Please open a GitHub Issue with:
  1.A minimal reproducible example or steps to trigger the bug 
  2.Expected vs. actual behaviour
  3.Python/Node version and OS

15. License

By contributing you agree that your changes will be released under the project's MIT License.

---

Again, thank you for helping to improve the Discrete Calabi–Yau Gauge Functor Dashboard!
