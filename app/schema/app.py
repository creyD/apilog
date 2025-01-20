from pydantic.json_schema import SkipJsonSchema

from app.schema.common import BaseSchemaModelIN, BaseSchemaModelOUT


class AppIN(BaseSchemaModelIN):
    name: str
    retention_days: int | SkipJsonSchema[None] = 30


class AppOUT(BaseSchemaModelOUT, AppIN):
    pass
