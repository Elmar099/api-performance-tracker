from fastapi import FastAPI
import time

app = FastAPI()


@app.get("/")
def home():
    return {"message": "API Performance Tracker is running!"}

@app.get("/api/users")
def get_users():
    return [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
        {"id": 3, "name": "Charlie"},
    ]

@app.get("/api/slow")
def slow_endpoint():
    time.sleep(2)
    return {"message": "This endpoint is slow!"}