"""Script to initialize and set up PostgreSQL instance for SQLModel tables."""

import logging
import os
import subprocess
import sys
import traceback
from pathlib import Path

import psycopg.errors
import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

from template_app.core import config

logger = logging.getLogger(__name__)


class DBInitError(Exception):
    pass


def get_alembic_config_dir() -> Path:
    """Get the directory containing alembic.ini."""
    # Try to find alembic.ini in multiple possible locations
    # to support both local development and container environments

    # Local development: back/ directory (4 levels up from this file)
    local_dev_path = Path(__file__).parent.parent.parent.parent

    # Container environment: alembic files should be at /app level
    container_path = Path("/app")

    # Docker/K8s alternative: check if alembic.ini is in current working directory or parent
    cwd_path = Path.cwd()

    # Try each path in order of preference
    for candidate_path in [local_dev_path, container_path, cwd_path, cwd_path.parent]:
        alembic_ini_path = candidate_path / "alembic.ini"
        if alembic_ini_path.exists():
            logger.info(f"Found alembic.ini at: {candidate_path}")
            return candidate_path

    return local_dev_path


def create_database_if_not_exists(postgres_db_uri: str, database_name: str):
    engine = create_engine(postgres_db_uri)
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        try:
            conn.execute(text(f'CREATE DATABASE "{database_name}"'))
        except ProgrammingError as e:
            if isinstance(e.orig, psycopg.errors.DuplicateDatabase):
                logger.info(f"{database_name} already exists")
                return True
            logger.error(f"❌ failed to create database {database_name}")
            return False
        except Exception:
            logger.error(f"❌ failed to create database {database_name}")
            return False
    logger.info(f"Created database {database_name}")
    return True


def run_migrations(db_uri: str) -> bool:
    """Set up the PostgreSQL database using Alembic migrations."""
    try:
        # Setup SQLModel tables using Alembic migrations
        logger.info("Setting up SQLModel tables using Alembic migrations...")
        alembic_dir = get_alembic_config_dir()

        # Run Alembic migrations to create/update database schema
        logger.info("Running Alembic migrations...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=alembic_dir,
            capture_output=True,
            text=True,
            env={**os.environ, "POSTGRESQL_URL": db_uri},
        )

        if result.returncode != 0:
            logger.error(f"❌ Failed to run Alembic migrations:\n{result.stderr}")
            return False
        else:
            logger.info(result.stdout)

        logger.info("✅ Database setup completed successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to set up database: {e}")
        traceback.print_exc()
        return False


def init_db():
    """Initialize PostgreSQL database for the template application."""
    logger.info("🚀 Starting PostgreSQL initialization...")

    db_url_string = config.POSTGRESQL_URL
    if db_url_string.startswith("postgresql://"):
        db_url_string = "postgresql+psycopg://" + db_url_string[len("postgresql://") :]

    db_url = sqlalchemy.engine.url.make_url(db_url_string)
    if not db_url.database:
        raise DBInitError("⚠️ Could not setup database: no target database found")

    postgres_db_uri = db_url.set(database="postgres")
    if not create_database_if_not_exists(
        postgres_db_uri.render_as_string(hide_password=False), db_url.database
    ):
        raise DBInitError("⚠️ Could not create database")

    if not run_migrations(db_url_string):
        raise DBInitError("⚠️ Could not setup database")

    logger.info("🎉 Database initialization completed successfully!")


def main():
    try:
        init_db()
    except DBInitError as e:
        logger.error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
