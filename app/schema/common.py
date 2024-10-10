from creyPY.fastapi.schemas.base import BaseSchemaModelOUT as TemplateOUT
from pydantic import BaseModel, ConfigDict


class BaseSchemaModelIN(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BaseSchemaModelOUT(BaseSchemaModelIN, TemplateOUT):
    pass
