.PHONY: help install lint format test test-cov run-backend run-frontend docker-up docker-down clean

PYTHON   := python3
PIP      := $(PYTHON) -m pip
UVICORN  := uvicorn
PYTEST   := $(PYTHON) -m pytest

# ── Help ──────────────────────────────────────────────────────────────────────
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Setup ─────────────────────────────────────────────────────────────────────
install: ## Install Python deps into active virtualenv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install black ruff pytest pytest-cov httpx

# ── Code quality ──────────────────────────────────────────────────────────────
format: ## Auto-format with black
	black main.py tests/

lint: ## Lint with ruff
	ruff check main.py tests/

# ── Tests ─────────────────────────────────────────────────────────────────────
test: ## Run test suite
	$(PYTEST) tests/ -v

test-cov: ## Run tests with coverage report
	$(PYTEST) tests/ -v --cov=main --cov-report=term-missing --cov-report=html

# ── Dev servers ───────────────────────────────────────────────────────────────
run-backend: ## Start FastAPI dev server on :8000
	$(UVICORN) main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Start Vite dev server on :5173
	npm run dev

# ── Docker ────────────────────────────────────────────────────────────────────
docker-up: ## Build and start all containers
	docker compose up --build

docker-down: ## Stop and remove containers
	docker compose down

# ── Clean ─────────────────────────────────────────────────────────────────────
clean: ## Remove build/cache artefacts
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name htmlcov -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name ".coverage" -delete
	rm -rf node_modules dist .vite
