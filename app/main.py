from fastapi import FastAPI
from database import check_dynamodb_connection

app = FastAPI()

@app.get("/")
def root():
    return {"status": "FastAPI OK"}

@app.get("/health")
def health():
    return {
        "fastapi": "ok",
        "dynamodb": check_dynamodb_connection()
    }