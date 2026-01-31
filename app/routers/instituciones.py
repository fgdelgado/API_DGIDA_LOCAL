from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import List, Optional

# Cliente DynamoDB
from database import get_dynamodb_client

# Modelos Pydantic
from models.institucion import (
    InstitucionCreate,
    InstitucionUpdate,
    InstitucionResponse,
    InstitucionListItem,
)

# Utilidad para generar IDs
from utils.id_generator import generate_id

# Router de FastAPI para instituciones
router = APIRouter(
    prefix="/instituciones",
    tags=["Instituciones"]
)

# Cliente DynamoDB
dynamodb = get_dynamodb_client()

# Nombre de la tabla DynamoDB
TABLE_NAME = "api_data"

@router.post("", response_model=InstitucionResponse)
def crear_institucion(data: InstitucionCreate):
    # Fecha actual en formato ISO
    now = datetime.utcnow().isoformat()

    # Generar ID con prefijo
    id_institucion = generate_id("INST-")

    # Item que se guardará en DynamoDB
    item = {
        "PK": f"INSTITUCION#{id_institucion}",  # Partition Key
        "SK": "METADATA",                      # Sort Key
        "id_institucion": id_institucion,
        **data.model_dump(),                   # Datos enviados por el cliente
        "enable": True,                        # Activa por defecto
        "fecha_creacion": now,
        "fecha_actualizacion": now,
    }

    # Guardar en DynamoDB
    dynamodb.put_item(
        TableName=TABLE_NAME,
        Item=item
    )

    # Devolver la institución creada
    return item

@router.get("/{id_institucion}", response_model=InstitucionResponse)
def obtener_institucion(id_institucion: str):
    # Buscar la institución por PK y SK
    response = dynamodb.get_item(
        TableName=TABLE_NAME,
        Key={
            "PK": f"INSTITUCION#{id_institucion}",
            "SK": "METADATA",
        },
    )

    # Si no existe, devolver error 404
    if "Item" not in response:
        raise HTTPException(
            status_code=404,
            detail="Institución no encontrada"
        )

    return response["Item"]

@router.get("", response_model=List[InstitucionListItem])
def listar_instituciones(
    enable: Optional[bool] = Query(None)
):
    # Scan (válido por ahora, luego se optimiza)
    response = dynamodb.scan(TableName=TABLE_NAME)
    items = response.get("Items", [])

    instituciones = []

    for item in items:
        # Solo tomamos instituciones (SK = METADATA)
        if item.get("SK") != "METADATA":
            continue

        # Filtrar por enable si viene en query
        if enable is not None and item.get("enable") != enable:
            continue

        # Devolver solo id y nombre
        instituciones.append({
            "id_institucion": item["id_institucion"],
            "nombre": item["nombre"],
        })

    return instituciones

@router.patch("/{id_institucion}", response_model=InstitucionResponse)
def actualizar_institucion(id_institucion: str, data: InstitucionUpdate):
    now = datetime.utcnow().isoformat()

    update_expression = []
    expression_values = {}

    # Construir dinámicamente el SET
    for field, value in data.model_dump(exclude_none=True).items():
        update_expression.append(f"{field} = :{field}")
        expression_values[f":{field}"] = value

    # Validar que haya algo para actualizar
    if not update_expression:
        raise HTTPException(
            status_code=400,
            detail="No hay campos para actualizar"
        )

    # Actualizar fecha
    update_expression.append(
        "fecha_actualizacion = :fecha_actualizacion"
    )
    expression_values[":fecha_actualizacion"] = now

    # Ejecutar actualización
    response = dynamodb.update_item(
        TableName=TABLE_NAME,
        Key={
            "PK": f"INSTITUCION#{id_institucion}",
            "SK": "METADATA",
        },
        UpdateExpression="SET " + ", ".join(update_expression),
        ExpressionAttributeValues=expression_values,
        ReturnValues="ALL_NEW",
    )

    return response["Attributes"]

@router.delete("/{id_institucion}")
def eliminar_institucion(id_institucion: str):
    now = datetime.utcnow().isoformat()

    # Delete lógico: solo se desactiva
    dynamodb.update_item(
        TableName=TABLE_NAME,
        Key={
            "PK": f"INSTITUCION#{id_institucion}",
            "SK": "METADATA",
        },
        UpdateExpression=(
            "SET enable = :enable, "
            "fecha_actualizacion = :fecha"
        ),
        ExpressionAttributeValues={
            ":enable": False,
            ":fecha": now,
        },
    )

    return {
        "message": "Institución desactivada correctamente"
    }
