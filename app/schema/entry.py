from app.schema.common import BaseSchemaModelIN, BaseSchemaModelOUT
from app.models.entry import TransactionType, LogType
from uuid import UUID
from pydantic.json_schema import SkipJsonSchema


class LogIN(BaseSchemaModelIN):
    application: UUID
    l_type: LogType = LogType.INFO
    t_type: TransactionType = TransactionType.UNDEFINED

    message: str | SkipJsonSchema[None] = None
    author: str = "system"
    object_reference: str | SkipJsonSchema[None] = None
    previous_object: dict | SkipJsonSchema[None] = None


class LogOUT(BaseSchemaModelOUT, LogIN):
    pass
