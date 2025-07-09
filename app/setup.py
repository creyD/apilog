import os
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from creyPY.fastapi.db.helpers import create_if_not_exists
from creyPY.fastapi.db.session import SQLALCHEMY_DATABASE_URL, get_db, name
from sqlalchemy.orm import Session

from alembic import command
from alembic.config import Config
from app.models.app import Application
from app.models.entry import LogEntry


def delete_old_logs(sess: Session | None = None):
    session = sess or next(get_db())

    for app in session.query(Application).filter(Application.retention_days.isnot(None)):
        cutoff = datetime.now() - timedelta(days=app.retention_days)
        print(
            f"Deleting logs older than {app.retention_days} days (cutoff: {cutoff}) for {app.name}",
        )
        session.query(LogEntry).filter(
            LogEntry.application == app.id, LogEntry.created_at < cutoff
        ).delete()

    session.commit()


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

    # Start retention deletion
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        delete_old_logs,
        "interval",
        id="deletor",
        days=1,
        max_instances=1,
        replace_existing=True,
        next_run_time=datetime.now(),
    )
    scheduler.start()
    print("Deletion scheduler started")
