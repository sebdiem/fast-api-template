pre-commit:
	uvx pre-commit run -c ../.pre-commit-config.yaml backend --all

test:
	@echo "Running tests..."
	uv run pytest -v

db:
	docker compose up postgres -d

clean-db:
	@echo "Cleaning database..."
	docker compose down postgres
	docker volume prune -f

reset-db: clean-db db
	@echo "Resetting database..."
	uv run init-db

dev-backend:
	@echo "Starting backend development server..."
	uv run init-db
	uv run fastapi dev src/template_app/main.py

dev: db dev-backend

migrate:
	@echo "Running database migrations..."
	alembic upgrade head

create-migration:
	@echo "Creating new migration..."
	@read -p "Enter migration message: " message; \
	alembic revision --autogenerate -m "$$message"

.PHONY: db dev-backend dev test test-coverage lint format type-check check migrate create-migration clean-db reset-db pre-commit install-pre-commit help
