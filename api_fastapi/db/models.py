# models.py

from sqlalchemy import Column, Integer, String, Float, JSON, TIMESTAMP, ARRAY
from db_orm.base import Base
from datetime import datetime



class ApiBenchmarkLog(Base):
    __tablename__ = "api_monitor"

    id = Column(Integer, primary_key=True)
    endpoint = Column(String)
    method = Column(String)
    status = Column(Integer)
    name = Column(String, nullable=True)
    key = Column(String, nullable=True)
    operation = Column(String, nullable=True)
    sources = Column(ARRAY(String), nullable=True)
    result = Column(JSON)
    elapsed = Column(Float)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)


class StoredResource(Base):
    __tablename__ = "stored_resources"

    name = Column(String, primary_key=True, index=True)
    data = Column(JSON, nullable=False)

    def __repr__(self):
        return f"<StoredResource(name={self.name})>"