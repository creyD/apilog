import os

from creyPY.fastapi.db.session import SQLALCHEMY_DATABASE_URL, name

from alembic import command
from alembic.config import Config
from app.services.db.session import create_if_not_exists


def setup(db_name=name):
    # Create Database
    create_if_not_exists(db_name)

    # Make alembic migrations
    config = Config()
    config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL + db_name)
    config.set_main_option(
        "script_location", os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic")
    )
    command.upgrade(config, "head")
