import importlib
import logging
from pathlib import Path
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from sqlmodel import SQLModel

logger = logging.getLogger(__name__)

load_dotenv()


def import_models():
    """Walk through the src folder to find models.py files.

    In our convention, this is where you place your SQLModel definitions.
    """
    root_path = (Path(__file__).parent.parent / "src").resolve()

    imported = set()

    for path, dirnames, filenames in root_path.walk():
        # If this directory contains a db.py file, import it as a module.
        if "models.py" in filenames:
            file_path = path / "models.py"
            module = ".".join(file_path.relative_to(root_path).with_suffix("").parts)
            if module and module not in imported:
                importlib.import_module(module)
                imported.add(module)
    if not imported:
        logger.warning("No models.py found, no migration could be generated")
    else:
        imported_models = "\n".join(sorted(imported))
        logger.info(f"The following models were imported:\n{imported_models}")


import_models()


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url():
    import os

    db_url = os.getenv("POSTGRESQL_URL")
    assert db_url, "Please specify POSTGRESQL_URL env var"
    if db_url.startswith("postgresql://"):
        return "postgresql+psycopg://" + db_url[len("postgresql://") :]
    return db_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
