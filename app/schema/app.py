from app.schema.common import BaseSchemaModelIN, BaseSchemaModelOUT


class AppIN(BaseSchemaModelIN):
    name: str


class AppOUT(BaseSchemaModelOUT, AppIN):
    pass
