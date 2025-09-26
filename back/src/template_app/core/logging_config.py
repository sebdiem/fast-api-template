import logging
import logging.config

from fastapi_cli.utils.cli import get_uvicorn_log_config

from template_app.core import config


def setup_logging() -> None:
    level = logging.DEBUG if config.DEBUG else logging.INFO
    log_config = get_uvicorn_log_config()
    log_config["loggers"]["template_app"] = {"handlers": ["default"], "level": "INFO"}
    logging.config.dictConfig(log_config)
    logging.getLogger().setLevel(level)
