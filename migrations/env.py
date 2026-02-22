import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# 1. Add your project root to sys.path so Alembic can resolve 'src' imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

# 2. Import ArchiPy's BaseEntity
from archipy.models.entities import BaseEntity

# 3. IMPORTANT: Import ALL your entity models here so they register with BaseEntity.metadata!
# Example based on your project structure:
import src.models.entities.user_entity

# 4. Import your runtime config to grab the DB URL dynamically
from src.configs.runtime_config import RuntimeConfig

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 5. Set target_metadata
target_metadata = BaseEntity.metadata


def get_database_url() -> str:
    configs = RuntimeConfig.global_config()
    return f"{configs.POSTGRES_SQLALCHEMY.DRIVER_NAME}://{configs.POSTGRES_SQLALCHEMY.USERNAME}:{configs.POSTGRES_SQLALCHEMY.PASSWORD}@{configs.POSTGRES_SQLALCHEMY.HOST}/{configs.POSTGRES_SQLALCHEMY.DATABASE}"


config.set_main_option("sqlalchemy.url", get_database_url())

# ... keep the rest of the default run_migrations_offline and run_migrations_online functions ...

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
