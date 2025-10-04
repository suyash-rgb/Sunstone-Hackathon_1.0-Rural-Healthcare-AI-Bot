# main.py
from fastapi import FastAPI

from app.core.config import settings

# Create a FastAPI "instance"
app = FastAPI()

# Define a path operation decorator (route)
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}