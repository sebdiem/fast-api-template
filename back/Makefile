PROJECT_NAME ?= fast_api_template
DB_SERVICE   ?= postgres
DB_VOLUME    ?= postgres_data

install:  ## Install dependencies
	cp -n .env.dist .env || true
	uv sync

pre-commit:  ## Run pre-commit checks
	uvx pre-commit run -c ../.pre-commit-config.yaml backend --all

test:  ## Run the tests
	@echo "Running tests..."
	uv run pytest -v

db:  ## Start a contenerized database
	docker compose -p $(PROJECT_NAME) up -d $(DB_SERVICE)

db-clean:  ## Stop the contenerized database
	@echo "Cleaning $(DB_SERVICE) data..."
	docker compose -p $(PROJECT_NAME) stop $(DB_SERVICE)
	docker compose -p $(PROJECT_NAME) rm -f $(DB_SERVICE)
	# Remove the named volume (project-scoped): <project>_<volume>
	docker volume rm $(PROJECT_NAME)_$(DB_VOLUME) || true

db-reset: db-clean db  ## Reset the database to an empty state
	@echo "Sleeping for 5 sec to let docker container initialize"
	@sleep 5
	@echo "Resetting database..."
	uv run init-db

db-migrate:  ## Migrate the database to the latest migration
	@echo "Running database migrations..."
	alembic upgrade head

db-create-migration: ## Sync alembic with model changes
	@echo "Creating new migration..."
	@read -p "Enter migration message: " message; \
	alembic revision --autogenerate -m "$$message"

dev-backend:  ## Run the development server
	@echo "Starting backend development server..."
	uv run fastapi dev src/template_app/main.py

dev: db dev-backend  ## Start the contenerize database and run the development server 


help: ## Print this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


.PHONY: install pre-commit test db db-clean db-reset db-migrate db-create-migration dev-backend dev help
