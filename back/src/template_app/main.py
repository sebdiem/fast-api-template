"""
Main FastAPI application with async support.
"""

import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from template_app.core import config
from template_app.core.database import close_db_connections, init_db_connections
from template_app.core.logging_config import setup_logging
from template_app.music.router import router as music_router

logger = logging.getLogger(__name__)

app: FastAPI | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle for async resources."""
    logger.info("Starting application lifespan...")
    await init_db_connections()
    logger.info("Application initialized.")
    yield
    logger.info("Shutting down application...")
    await close_db_connections()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    logger.info("Creating FastAPI app")

    app = FastAPI(
        title="Template App",
        description="FastAPI template with domain-driven architecture",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(music_router)

    # Health check endpoint
    @app.get("/health")
    async def health():
        return {"status": "OK", "environment": config.ENV}

    logger.info("FastAPI app created successfully")
    return app


if config.ENV != "test":
    app = create_app()


if __name__ == "__main__":
    setup_logging()
    app = create_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8001")),
    )
