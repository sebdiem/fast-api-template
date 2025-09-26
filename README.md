# FastAPI Template - Domain-Driven Architecture

A production-ready FastAPI template with domain-driven architecture, featuring async PostgreSQL, comprehensive testing, and modern Python tooling.

## Features

- **Domain-Driven Architecture**: Clean separation between core infrastructure and business domains
- **Async PostgreSQL**: Full async database support with SQLModel and SQLAlchemy 2.0
- **Comprehensive Testing**: Test factories, fixtures, and database isolation
- **Modern Tooling**: Ruff for linting/formatting, mypy for type checking, pytest for testing
- **Database Migrations**: Alembic for schema versioning
- **Pre-commit Hooks**: Automated code quality checks
- **Docker Support**: PostgreSQL development environment
- **Example Domain**: Complete music domain with bands and musicians

## Project Structure

```
fast_api_template/
├── back/                          # Backend application
│   ├── src/template_app/
│   │   ├── main.py                # FastAPI app factory
│   │   ├── core/                  # Cross-domain infrastructure
│   │   │   ├── config.py          # Environment configuration
│   │   │   ├── logging_config.py  # Logging setup
│   │   │   ├── exceptions.py      # Common exceptions
│   │   │   └── database/          # Database infrastructure
│   │   │       ├── base.py        # Async SQLAlchemy setup
│   │   │       └── models.py      # Base model classes
│   │   ├── music/                 # Example domain
│   │   │   ├── models.py          # Band, Musician models
│   │   │   ├── router.py          # Music API endpoints
│   │   │   ├── service.py         # Business logic
│   │   │   └── schemas.py         # Pydantic request/response models
│   │   └── commands/
│   │       └── init_db.py         # Database initialization
│   ├── tests/
│   │   ├── conftest.py            # Test fixtures and configuration
│   │   ├── core/                  # Core test utilities
│   │   │   ├── factories/
│   │   │   │   └── base.py        # SQLModelFaker for test data
│   │   │   └── utils/
│   │   │       └── db.py          # Test database utilities
│   │   └── music/                 # Music domain tests
│   │       ├── factories.py       # Music-specific test factories
│   │       ├── test_models.py     # Model tests
│   │       └── test_router.py     # API endpoint tests
│   ├── alembic/                   # Database migrations
│   ├── pyproject.toml             # Dependencies & tooling config
│   ├── .pre-commit-config.yaml    # Backend-specific hooks
│   ├── Makefile                   # Development commands
│   ├── docker-compose.yml         # PostgreSQL for development
│   ├── alembic.ini                # Migration configuration
│   ├── .env.dist                  # Environment template
│   └── .env.test                  # Test environment config
├── .pre-commit-config.yaml        # Root-level pre-commit config
└── README.md                      # This file
```

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Docker and Docker Compose
- PostgreSQL (via Docker)

### Setup

1. **Clone or copy this template**:
   ```bash
   cp -r fast_api_template/ my-new-project/
   cd my-new-project/back/
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   # or with pip: pip install -e .
   ```

3. **Set up environment**:
   ```bash
   cp .env.dist .env
   # Edit .env with your configuration
   ```

4. **Start the database**:
   ```bash
   make db
   # or: docker compose up postgres -d
   ```

5. **Initialize the database**:
   ```bash
   uv run init-db
   # or: make migrate
   ```

6. **Run the development server**:
   ```bash
   make dev-backend
   # or: uv run fastapi dev src/template_app/main.py
   ```

7. **Visit the API**:
   - API: http://localhost:8000
   - Health check: http://localhost:8000/health
   - Interactive docs: http://localhost:8000/docs

## Development

### Available Commands

```bash
make help                 # Show all available commands
make dev                  # Start database and backend
make test                 # Run tests
make test-coverage        # Run tests with coverage
make lint                 # Run linting
make format               # Format code
make type-check           # Run type checks
make check                # Run all checks (lint, type-check, test)
make migrate              # Run database migrations
make create-migration     # Create new migration
make reset-db             # Reset database and run migrations
```

### Testing

The template includes comprehensive testing infrastructure:

- **Database isolation**: Each test runs in a transaction that's rolled back
- **Test factories**: Realistic fake data generation with Faker
- **HTTP client**: Async test client for API testing
- **Fixtures**: Reusable test components

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test file
uv run pytest tests/music/test_router.py -v

# Run with database output (for debugging)
uv run pytest tests/music/test_router.py -v -s
```

### Code Quality

The template enforces code quality through:

- **Ruff**: Fast linting and formatting
- **mypy**: Static type checking
- **Pre-commit hooks**: Automated checks on commit

```bash
# Set up pre-commit hooks
make install-pre-commit

# Run all code quality checks
make check

# Format code
make format
```

### Database Migrations

Create and run migrations with Alembic:

```bash
# Create a new migration
make create-migration
# Follow the prompt to enter a migration message

# Run migrations
make migrate

# Reset database (useful in development)
make reset-db
```

## API Example

The template includes a complete music domain example:

### Bands

```bash
# Create a band
curl -X POST "http://localhost:8000/api/music/bands" \
  -H "Content-Type: application/json" \
  -d '{"name": "The Beatles", "genre": "Rock", "formed_year": 1960, "country": "UK"}'

# Get all bands
curl "http://localhost:8000/api/music/bands"

# Get bands by genre
curl "http://localhost:8000/api/music/bands?genre=Rock"

# Get specific band
curl "http://localhost:8000/api/music/bands/1"

# Update a band
curl -X PATCH "http://localhost:8000/api/music/bands/1" \
  -H "Content-Type: application/json" \
  -d '{"genre": "Pop Rock"}'

# Delete a band
curl -X DELETE "http://localhost:8000/api/music/bands/1"
```

### Musicians

```bash
# Create a musician
curl -X POST "http://localhost:8000/api/music/musicians" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Lennon", "instrument": "Guitar", "band_id": 1}'

# Get all musicians
curl "http://localhost:8000/api/music/musicians"

# Get musicians by band
curl "http://localhost:8000/api/music/musicians?band_id=1"
```

## Adding New Domains

To add a new domain (e.g., `products`):

1. **Create domain structure**:
   ```bash
   mkdir -p src/template_app/products
   touch src/template_app/products/{__init__.py,models.py,router.py,service.py,schemas.py}
   ```

2. **Create domain models** (in `models.py`):
   ```python
   from template_app.core.database.models import BaseModel
   from sqlmodel import Field

   class Product(BaseModel, table=True):
       name: str = Field(index=True)
       price: float
       description: str | None = None
   ```

3. **Add router** (in `router.py`) following the music domain pattern

4. **Include in main app** (in `main.py`):
   ```python
   from template_app.products.router import router as products_router

   app.include_router(products_router)
   ```

5. **Create tests**:
   ```bash
   mkdir -p tests/products
   touch tests/products/{__init__.py,factories.py,test_models.py,test_router.py}
   ```

6. **Generate migration**:
   ```bash
   make create-migration
   # Enter: "Add products domain"
   ```

## Architecture Principles

### Domain-Driven Design

- **Core**: Cross-domain infrastructure (database, config, logging)
- **Domains**: Business logic organized by domain (music, products, etc.)
- **Clear boundaries**: Each domain is self-contained with its own models, services, and routers

### Async-First

- Full async/await support
- Async database operations with SQLModel
- Async HTTP client for testing

### Testing Strategy

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test API endpoints with database
- **Test factories**: Generate realistic test data
- **Database isolation**: Each test gets a clean database state

### Code Quality

- **Type safety**: Full mypy type checking
- **Code formatting**: Consistent style with Ruff
- **Pre-commit hooks**: Catch issues before commit
- **Dependency management**: Modern Python tooling with uv

## Environment Configuration

The template supports multiple environments through environment variables:

- **Development**: `.env` file with `ENV=dev`
- **Testing**: `.env.test` file with `ENV=test`
- **Production**: Environment variables with `ENV=prod`

Key configuration options:

- `POSTGRESQL_URL`: Database connection string
- `SECRET_KEY`: Session encryption key
- `DEBUG`: Enable debug logging
- `ALLOWED_ORIGINS`: CORS configuration

## Production Deployment

For production deployment:

1. Set environment variables (don't use `.env` files)
2. Use a production database (not Docker)
3. Set `ENV=prod` and `DEBUG=false`
4. Use a proper secret key
5. Configure proper CORS origins
6. Run migrations: `uv run init-db`
7. Use a production ASGI server like Gunicorn with Uvicorn workers

## Contributing

1. Follow the established patterns in the music domain
2. Add tests for new functionality
3. Run `make check` before committing
4. Use conventional commit messages
5. Update documentation as needed

## License

This template is provided as-is for educational and development purposes. Adapt it according to your project's needs and license requirements.