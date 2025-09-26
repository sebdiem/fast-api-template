import os
from pathlib import Path

from dotenv import load_dotenv

_IS_PYTEST_RUNNING = os.getenv("IS_PYTEST_RUNNING")  # set in conftest.py
if _IS_PYTEST_RUNNING:
    load_dotenv(".env.test")
else:
    load_dotenv()

ENV = "test" if _IS_PYTEST_RUNNING else os.getenv("ENV", "dev")
SITE_URL = os.getenv("SITE_URL", "http://localhost:8000")

PACKAGE_ROOT_DIR = Path(__file__).parent.parent
PROJECT_ROOT_DIR = Path(__file__).parent.parent.parent.parent


# Database
POSTGRESQL_URL = os.getenv(
    "POSTGRESQL_URL", "postgresql://user:password@localhost:5432/template_app"
)

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

# CORS
ALLOWED_ORIGINS = [SITE_URL]
if ENV in ("dev", "test"):
    ALLOWED_ORIGINS = list(
        {
            *ALLOWED_ORIGINS,
            *[
                f"http://{host}:{port}"
                for host in ("127.0.0.1", "localhost")
                for port in ("8000", "5173", "3000")
            ],
        }
    )

# Debug mode
DEBUG = ENV in ("test", "dev") and os.getenv("DEBUG", "false").lower() == "true"
