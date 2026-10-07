from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.k6_runner import run_k6_test
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime, timezone
from uuid import uuid4
from backend.database import SessionLocal
from backend.models import Test
import time


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    url: str
    vus: int = Field(gt=0, le=1000)
    duration: str
    p95_threshold_ms: float = Field(gt=0)

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, value):
        if not value.endswith(("s", "m")):
            raise ValueError("Duration must end with 's' or 'm'")

        return value

class TestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    status: str
    error_message: Optional[str] = None
    p95_threshold_ms: Optional[float] = None

    url: str
    vus: int
    duration: str
    requests: Optional[int] = None
    requests_per_second: Optional[float] = None
    avg_latency_ms: Optional[float] = None
    p95_latency_ms: Optional[float] = None
    max_latency_ms: Optional[float] = None
    failure_rate: Optional[float] = None
    threshold_passed: Optional[bool] = None

def execute_test(test_id, url, vus, duration, p95_threshold_ms):
    db = SessionLocal()

    try:
        result = run_k6_test(url, vus, duration, p95_threshold_ms)

        if result["failure_rate"] == 1.0:
            test = db.query(Test).filter(Test.id == test_id).first()

            if test:

                test.status = "failed"
                test.error_message = "All HTTP requests failed"

                test.requests = result["requests"]
                test.requests_per_second = result["requests_per_second"]
                test.avg_latency_ms = result["avg_latency_ms"]
                test.p95_latency_ms = result["p95_latency_ms"]
                test.max_latency_ms = result["max_latency_ms"]
                test.failure_rate = result["failure_rate"]
                test.threshold_passed = result["threshold_passed"]

                db.commit()

            return

        test = db.query(Test).filter(Test.id == test_id).first()

        if test:

            test.status = "completed"
            test.requests = result["requests"]
            test.requests_per_second = result["requests_per_second"]
            test.avg_latency_ms = result["avg_latency_ms"]
            test.p95_latency_ms = result["p95_latency_ms"]
            test.max_latency_ms = result["max_latency_ms"]
            test.failure_rate = result["failure_rate"]
            test.threshold_passed = result["threshold_passed"]

            db.commit()

    except Exception as error:

        test = db.query(Test).filter(Test.id == test_id).first()

        if test:
            test.status = "failed"
            test.error_message = str(error)
            db.commit()

    finally:
        db.close()

@app.post("/api/tests")
def run_test(config: TestConfig, background_tasks: BackgroundTasks):
    test_id = str(uuid4())
    created_at = datetime.now(timezone.utc)

    db = SessionLocal()

    test = Test(
        id=test_id,
        created_at=created_at,
        status="running",
        url=config.url,
        vus=config.vus,
        duration=config.duration,
        p95_threshold_ms=config.p95_threshold_ms,
    )

    db.add(test)
    db.commit()
    db.close()

    background_tasks.add_task(
        execute_test,
        test_id,
        config.url,
        config.vus,
        config.duration,
        config.p95_threshold_ms,
    )

    return {
        "test_id": test_id,
        "created_at": created_at.isoformat(),
        "status": "running",
        "config": {
            "url": config.url,
            "vus": config.vus,
            "duration": config.duration,
        },
    }

@app.get("/api/tests", response_model=list[TestResponse])
def get_tests():
    db = SessionLocal()

    tests = db.query(Test).order_by(Test.created_at.desc()).all()

    db.close()

    return tests

@app.get("/api/tests/{test_id}", response_model=TestResponse)
def get_test(test_id: str):
    db = SessionLocal()

    test = db.query(Test).filter(Test.id == test_id).first()

    db.close()

    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    return test