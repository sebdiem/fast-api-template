"""Script to initialize and set up PostgreSQL instance for SQLModel tables."""

import logging
import subprocess
import sys
import traceback
from pathlib import Path

import click

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


def setup_database(db_uri: str) -> bool:
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
        )

        if result.returncode != 0:
            logger.error(f"❌ Failed to run Alembic migrations: {result.stderr}")
            return False

        logger.info("✅ Database setup completed successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to set up database: {e}")
        traceback.print_exc()
        return False


def init_db():
    """Initialize PostgreSQL database for the template application."""
    logger.info("🚀 Starting PostgreSQL initialization...")

    if not setup_database(config.POSTGRESQL_URL):
        raise DBInitError("⚠️ Could not setup database")

    logger.info("🎉 Database initialization completed successfully!")


@click.command()
def main():
    try:
        init_db()
    except DBInitError as e:
        logger.error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
