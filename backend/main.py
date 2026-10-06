from fastapi import FastAPI
from backend.k6_runner import run_k6_test
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from uuid import uuid4
from backend.database import SessionLocal
from backend.models import Test
import time


app = FastAPI()


@app.get("/")
def home():
    return {"message": "API Performance Tracker is running!"}

@app.get("/api/users")
def get_users(limit: int = 3):
    users = []

    for i in range(1, limit + 1):
        users.append({
            "id": i,
            "name": f"User {i}"
        })

    return users

@app.get("/api/products")
def get_products():
    products = [
        {"id": 1, "name": "Laptop", "price": 1200},
        {"id": 2, "name": "Keyboard", "price": 100},
        {"id": 3, "name": "Mouse", "price": 50},
        {"id": 4, "name": "Monitor", "price": 400},
    ]

    return products

@app.get("/api/slow")
def slow_endpoint():
    time.sleep(1)
    return {"message": "This endpoint is slow!"}


class TestConfig(BaseModel):
    vus: int = Field(gt=0, le=1000)
    duration: str

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, value):
        if not value.endswith(("s", "m")):
            raise ValueError("Duration must end with 's' or 'm'")

        return value

@app.post("/api/tests")
def run_test(config: TestConfig):
    result = run_k6_test(config.vus, config.duration)

    test_id = str(uuid4())
    created_at = datetime.now(timezone.utc)

    db = SessionLocal()

    test = Test(
        id=test_id,
        created_at=created_at,
        vus=config.vus,
        duration=config.duration,
        requests=result["requests"],
        requests_per_second=result["requests_per_second"],
        avg_latency_ms=result["avg_latency_ms"],
        p95_latency_ms=result["p95_latency_ms"],
        max_latency_ms=result["max_latency_ms"],
        failure_rate=result["failure_rate"],
    )

    db.add(test)
    db.commit()
    db.close()

    return {
        "test_id": test_id,
        "created_at": created_at.isoformat(),
        "config": {
            "vus": config.vus,
            "duration": config.duration,
        },
        "results": result,
    }

@app.get("/api/tests")
def get_tests():
    db = SessionLocal()

    tests = db.query(Test).order_by(Test.created_at.desc()).all()

    db.close()

    return tests