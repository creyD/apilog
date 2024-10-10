from creyPY.fastapi.models.base import Base
from sqlalchemy import Column, String


class Application(Base):
    name = Column(String(512), nullable=False, unique=True)
