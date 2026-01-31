from fastapi import FastAPI
from database import check_dynamodb_connection
from routers.instituciones import router as instituciones_router

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
app.include_router(instituciones_router)