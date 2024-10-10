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
    environment = Column(String(64), nullable=True, default="prod")
    # type of the log entry
    l_type = Column(Enum(LogType), nullable=False, default=LogType.INFO)
    # type of the transaction
    t_type = Column(Enum(TransactionType), nullable=False, default=TransactionType.UNDEFINED)
    # a custom logmessage
    message = Column(String(512), nullable=True)
    # author ID i.e. auth0 user sub
    author = Column(String(512), nullable=False, default="system")
    # optional reference to the object (like object ID)
    object_reference = Column(String(512), nullable=True)
    # for irreversible operations, store the object state before the operation
    previous_object = Column(JSON, nullable=True)
