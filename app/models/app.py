from creyPY.fastapi.models.base import Base
from sqlalchemy import Column, Integer, String


class Application(Base):
    name = Column(String(512), nullable=False, unique=True)
    retention_days = Column(Integer, nullable=True, default=30)
