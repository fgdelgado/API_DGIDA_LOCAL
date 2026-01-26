# API_DGIDA_LOCAL

API backend desarrollada con **FastAPI** usando **DynamoDB Local** para pruebas en entorno local mediante **Docker**.

Este proyecto sirve como base para construir un CRUD que luego puede migrarse fácilmente a **AWS (API Gateway + Lambda + DynamoDB)**.

---

## Tecnologías usadas

- Python 3.11
- FastAPI
- DynamoDB Local
- Docker & Docker Compose
- Boto3 (AWS SDK para Python)

---

## Estructura del proyecto

```
API_DGIDA_LOCAL/
├── app/
│   ├── main.py          # Punto de entrada de FastAPI
│   ├── database.py      # Conexión a DynamoDB
│   ├── routes.py        # Endpoints de la API
│   ├── models.py        # Modelos de datos (Pydantic)
│   └── requirements.txt # Dependencias
│
├── .env.example         # Variables de entorno de ejemplo
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Requisitos

Antes de empezar asegúrate de tener instalado:

- Docker
- Docker Compose
- Git
- AWS CLI

---

## Variables de entorno

Copia el archivo `.env.example` y crea un archivo `.env`:

```bash
cp .env.example .env
```

Variables principales:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `DYNAMODB_ENDPOINT_URL`

---

## Cómo levantar el proyecto en local

Desde la carpeta raíz del proyecto:

```bash
docker compose build
docker compose up
```

La API estará disponible en:

- http://localhost:8000
- Documentación Swagger: http://localhost:8000/docs

---

## Endpoint de estado (health check)

Para verificar que todo está funcionando:

```
GET /health
```

Respuesta esperada:

```json
{
  "fastapi": "ok",
  "dynamodb": "ok"
}
```

---

## Estado del proyecto

FastAPI funcionando  
DynamoDB Local conectado  
CRUD en desarrollo  

---

## Futuro despliegue en AWS

Este proyecto está diseñado para migrar a:

- AWS Lambda
- API Gateway
- DynamoDB (real)

Minimizando cambios en el código.

