from fastapi import FastAPI
from backend.k6_runner import run_k6_test
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

@app.post("/api/tests")
def run_test():
    result = run_k6_test()

    return {
        "success": result["success"],
        "output": result["output"],
        "error": result["error"],
    }