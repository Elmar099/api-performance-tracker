from sqlalchemy import Column, Integer, Float, String, DateTime
from backend.database import Base


class Test(Base):
    __tablename__ = "tests"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime)

    url = Column(String)

    vus = Column(Integer)
    duration = Column(String)

    requests = Column(Integer)
    requests_per_second = Column(Float)
    avg_latency_ms = Column(Float)
    p95_latency_ms = Column(Float)
    max_latency_ms = Column(Float)
    failure_rate = Column(Float)