from fastapi import FastAPI
from database import check_dynamodb_connection
from routers.instituciones import router as instituciones_router
from routers.tramites import router as tramites_router
from routers.proyectos import router as proyectos_router
from routers.programas import router as programas_router

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
app.include_router(tramites_router)
app.include_router(proyectos_router)
app.include_router(programas_router)