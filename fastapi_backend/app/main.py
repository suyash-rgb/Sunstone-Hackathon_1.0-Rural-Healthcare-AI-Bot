# main.py
from fastapi import FastAPI

# Create a FastAPI "instance"
app = FastAPI()

# Define a path operation decorator (route)
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}