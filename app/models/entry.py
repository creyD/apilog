from creyPY.fastapi.models.base import Base
from sqlalchemy import Column, String, ForeignKey, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID

from enum import Enum as pyenum


class TransactionType(pyenum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    UNDEFINED = "undefined"


class LogType(pyenum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogEntry(Base):
    application = Column(
        UUID(as_uuid=True), ForeignKey("application.id", ondelete="CASCADE"), nullable=False
    )

    t_type = Column(Enum(TransactionType), nullable=False, default=TransactionType.UNDEFINED)
    l_type = Column(Enum(LogType), nullable=False, default=LogType.INFO)

    message = Column(String(512), nullable=True)
    author = Column(String(512), nullable=False, default="system")

    previous_object = Column(JSON, nullable=True)
