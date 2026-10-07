from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from backend.database import Base


class Test(Base):
    __tablename__ = "tests"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime)
    status = Column(String, default="pending")
    error_message = Column(String, nullable=True)

    url = Column(String)
    vus = Column(Integer)
    duration = Column(String)
    p95_threshold_ms = Column(Float)

    requests = Column(Integer)
    requests_per_second = Column(Float)
    avg_latency_ms = Column(Float)
    p95_latency_ms = Column(Float)
    max_latency_ms = Column(Float)
    failure_rate = Column(Float)
    threshold_passed = Column(Boolean)