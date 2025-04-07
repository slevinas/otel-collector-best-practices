from sqlalchemy import Column, Integer, String, Float, JSON, TIMESTAMP, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Benchmark(Base):
    __tablename__ = "benchmarks"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String, nullable=False)        # e.g. /store/A
    method = Column(String, nullable=True)           # GET, POST, PUT
    status = Column(Integer, nullable=True)          # 200, 400, 500, etc.
    name = Column(String, nullable=True)             # Resource name (e.g., A)
    key = Column(String, nullable=True)              # Nested key if applicable (e.g., x.value)
    operation = Column(String, nullable=True)        # add, subtract, etc.
    sources = Column(ARRAY(String), nullable=True)   # e.g., ['A', 'B']
    result = Column(JSON, nullable=True)             # Resulting JSON payload
    elapsed = Column(Float, nullable=True)           # Time taken in seconds
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
