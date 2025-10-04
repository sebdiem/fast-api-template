# ruff: noqa: E402

import os
import sys

assert "garage.config" not in sys.modules, (
    "Including any module above this line will break config loading in tests."
)
os.environ["IS_PYTEST_RUNNING"] = "true"

import logging
import os
import random
from collections.abc import AsyncGenerator
from unittest.mock import patch

import pytest
from faker import Faker
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool, create_engine, event, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from template_app.commands.init_db import init_db as init_db_command
from template_app.core import config
from template_app.core.database.base import SESSION_OPTIONS
from template_app.main import create_app, lifespan
from tests.core.factories.base import SQLModelFaker
from tests.core.utils.db import increment_query_count

# Mark as pytest environment
os.environ["IS_PYTEST_RUNNING"] = "true"

logger = logging.getLogger(__name__)

SESSION_TEST_SEED = random.randint(0, 100000)


def pytest_configure() -> None:
    logger.info(f"Starting test session with seed {SESSION_TEST_SEED}")


@pytest.fixture(scope="function", autouse=True)
def cleanup_http_connections():
    """Automatically cleanup HTTP connections after each test."""
    import gc

    yield  # Run the test

    gc.collect()


def pytest_addoption(parser):
    parser.addoption(
        "--allow-db-drop",
        action="store_true",
        default=False,
        help="Allow dropping the target PostgreSQL database if it already exists.",
    )


def _db_exists(conn, db_name: str) -> bool:
    return bool(
        conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": db_name},
        ).scalar()
    )


def _terminate_connections(conn, db_name: str):
    conn.execute(
        text(
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
            "WHERE datname = :name AND pid <> pg_backend_pid()"
        ),
        {"name": db_name},
    )


@pytest.fixture(scope="session")
def create_db(request):
    """Fixture that ensures a fresh test database exists, yields its URL, and drops it after."""

    url = config.POSTGRESQL_URL
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://") :]
    db_name = make_url(url).database
    maintenance_db = make_url(url).set(
        database="postgres"
    )  # this db is used to perform the drop / createdb operations
    engine = create_engine(maintenance_db, poolclass=NullPool)

    if not db_name or not (db_name.endswith("_test") or db_name.startswith("test_")):
        raise RuntimeError(
            f'Safety check: refusing to manage database "{db_name}". '
            'Use a name ending with "_test" or starting with "test_".'
        )

    with engine.connect() as conn:
        conn = conn.execution_options(isolation_level="AUTOCOMMIT")
        exists = _db_exists(conn, db_name)
        if exists:
            can_drop = request.config.getoption("--allow-db-drop")
            if not can_drop:
                raise RuntimeError(
                    f'Target database "{db_name}" already exists.\n'
                    "Refusing to drop it without confirmation.\n"
                    "Use --allow-db-drop to allow drop.\n\n"
                )

        _terminate_connections(conn, db_name)
        conn.execute(text(f'DROP DATABASE IF EXISTS "{db_name}" WITH (FORCE)'))

    # Create database
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        conn.execute(text(f'CREATE DATABASE "{db_name}"'))
        created_by_fixture = True

    # Yield the URL for tests to use
    try:
        yield str(url)
    finally:
        # Only clean up if we created it (so we don't nuke someone's dev DB unexpectedly)
        if created_by_fixture:
            with engine.connect() as conn:
                conn = conn.execution_options(isolation_level="AUTOCOMMIT")
                _terminate_connections(conn, db_name)
                conn.execute(text(f'DROP DATABASE IF EXISTS "{db_name}" WITH (FORCE)'))

        # Always dispose of the engine to clean up connections
        engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def init_db(create_db):
    init_db_command()
    return create_db


@pytest.fixture(scope="session")
async def engine(init_db, request):
    # Enable SQL logging based on pytest verbosity level
    # -v or higher enables SQL logging
    verbose = request.config.getoption("verbose") >= 1
    engine = create_async_engine(init_db, future=True, echo=verbose, poolclass=NullPool)

    # Add event listener to count queries
    @event.listens_for(engine.sync_engine, "before_execute")
    def count_queries(conn, clauseelement, multiparams, params, execution_options):
        increment_query_count(clauseelement)

    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture
async def use_db(engine):
    """This fixture should be used anytime a test touches the db."""
    # Create test transaction that will be rolled back
    async with engine.begin() as conn:
        trans = await conn.begin_nested()

        def mock_session_local():
            return async_sessionmaker(bind=conn, **SESSION_OPTIONS)()  # type: ignore

        with patch(
            "template_app.core.database.base.SessionLocal",
            side_effect=mock_session_local,
        ):
            try:
                yield
            finally:
                await trans.rollback()


@pytest.fixture
def app(use_db) -> FastAPI:
    app = create_app()
    return app


@pytest.fixture
async def db_session(use_db) -> AsyncGenerator[AsyncSession]:
    from template_app.core.database.base import SessionLocal

    async with SessionLocal() as session:
        yield session


@pytest.fixture
async def http_client(request, app) -> AsyncGenerator[AsyncClient]:
    """Fixture that provides an AsyncClient bound to the Starlette app."""
    run_lifespan = request.node.get_closest_marker("run_lifespan") is not None
    if run_lifespan:
        # Runs startup before yielding; runs shutdown after the test
        async with lifespan(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://testserver"
            ) as ac:
                yield ac
    else:
        # No lifespan: cheap client for tests that don't need startup/shutdown
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            yield ac


@pytest.fixture
async def factory(db_session) -> AsyncGenerator[SQLModelFaker]:
    """Database factory for creating persisted model instances in tests.

    Provides an :class:`SQLModelFaker` instance that automatically persists
    created models to the test database with transaction isolation.

    Usage:
        from tests.music.factories import create_band

        async def test_something(factory):
            band = await create_band(factory, name="The Beatles")
    """
    Faker.seed(SESSION_TEST_SEED)
    faker = Faker()
    yield SQLModelFaker(faker, db_session)
