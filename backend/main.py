from fastapi import FastAPI
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
    time.sleep(2)
    return {"message": "This endpoint is slow!"}