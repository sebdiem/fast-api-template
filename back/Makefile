db:
	docker compose up postgres -d

dev-backend:
	@echo "Starting backend development server..."
	uv run init-db
	uv run fastapi dev src/template_app/main.py

dev: db dev-backend

test:
	@echo "Running tests..."
	uv run pytest -v

test-coverage:
	@echo "Running tests with coverage..."
	uv run pytest --cov=src/template_app --cov-report=html --cov-report=term -v

lint:
	@echo "Running linting..."
	uv run ruff check .
	uv run ruff format --check .

format:
	@echo "Formatting code..."
	uv run ruff format .

type-check:
	@echo "Running type checks..."
	uv run mypy src

check: lint type-check test

migrate:
	@echo "Running database migrations..."
	alembic upgrade head

create-migration:
	@echo "Creating new migration..."
	@read -p "Enter migration message: " message; \
	alembic revision --autogenerate -m "$$message"

clean-db:
	@echo "Cleaning database..."
	docker compose down postgres
	docker volume prune -f

reset-db: clean-db db
	@echo "Resetting database..."
	uv run init-db

pre-commit:
	uvx pre-commit run --all-files

install-pre-commit:
	uvx pre-commit install

help:
	@echo "Available commands:"
	@echo "  db              - Start PostgreSQL with Docker Compose"
	@echo "  dev-backend     - Start backend development server"
	@echo "  dev             - Start database and backend"
	@echo "  test            - Run tests"
	@echo "  test-coverage   - Run tests with coverage report"
	@echo "  lint            - Run linting checks"
	@echo "  format          - Format code"
	@echo "  type-check      - Run type checks"
	@echo "  check           - Run all checks (lint, type-check, test)"
	@echo "  migrate         - Run database migrations"
	@echo "  create-migration - Create new migration"
	@echo "  clean-db        - Clean database containers and volumes"
	@echo "  reset-db        - Reset database and run migrations"
	@echo "  pre-commit      - Run pre-commit hooks"
	@echo "  install-pre-commit - Install pre-commit hooks"
	@echo "  help            - Show this help message"

.PHONY: db dev-backend dev test test-coverage lint format type-check check migrate create-migration clean-db reset-db pre-commit install-pre-commit help