from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import create_engine

from alembic import context

load_dotenv()


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Our models
from app.services.db.models import Base

target_metadata = Base.metadata


def run_migrations() -> None:
    from creyPY.fastapi.db.session import SQLALCHEMY_DATABASE_URL, name

    with create_engine(SQLALCHEMY_DATABASE_URL + name, pool_pre_ping=True).connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations()
