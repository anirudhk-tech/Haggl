# =============================================================================
# Haggl - Development Makefile
# =============================================================================

.PHONY: help install dev test lint format typecheck clean docker-build docker-up docker-down

# Default target
help:
	@echo "Haggl Development Commands"
	@echo "=========================="
	@echo ""
	@echo "Setup:"
	@echo "  make install      Install all dependencies"
	@echo "  make dev          Start development servers"
	@echo ""
	@echo "Testing:"
	@echo "  make test         Run all tests"
	@echo "  make test-cov     Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint         Run linters"
	@echo "  make format       Format code"
	@echo "  make typecheck    Run type checker"
	@echo "  make check        Run all checks"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build Build Docker images"
	@echo "  make docker-up    Start containers"
	@echo "  make docker-down  Stop containers"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean        Clean build artifacts"
	@echo "  make docs         Generate documentation"

# =============================================================================
# Setup
# =============================================================================

install:
	pip install -e ".[dev]"
	cd frontend && npm install

dev:
	@echo "Starting backend..."
	python main.py &
	@echo "Starting frontend..."
	cd frontend && npm run dev

# =============================================================================
# Testing
# =============================================================================

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term
	@echo "Coverage report: htmlcov/index.html"

test-watch:
	pytest-watch tests/

# =============================================================================
# Code Quality
# =============================================================================

lint:
	ruff check src/
	cd frontend && npm run lint

format:
	ruff format src/
	cd frontend && npx prettier --write "**/*.{ts,tsx,js,json,css}"

typecheck:
	mypy src/ --ignore-missing-imports
	cd frontend && npx tsc --noEmit

check: lint typecheck test
	@echo "All checks passed! ✅"

# =============================================================================
# Docker
# =============================================================================

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-shell:
	docker-compose exec backend /bin/bash

# =============================================================================
# Utilities
# =============================================================================

clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	rm -rf src/**/__pycache__ src/**/**/__pycache__
	rm -rf frontend/.next frontend/node_modules/.cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

docs:
	@echo "Documentation available in /docs"
	@echo "  - docs/ARCHITECTURE.md"
	@echo "  - docs/API.md"

# =============================================================================
# Database
# =============================================================================

db-shell:
	mongosh "$(MONGODB_URI)"

db-seed:
	python scripts/seed_data.py

# =============================================================================
# Release
# =============================================================================

version:
	@python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])"

release-patch:
	bump2version patch

release-minor:
	bump2version minor

release-major:
	bump2version major
