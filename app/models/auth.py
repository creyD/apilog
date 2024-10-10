from creyPY.fastapi.models.base import Base
from sqlalchemy import Column, String


class APIKey(Base):
    note = Column(String(512), nullable=False, unique=True)
