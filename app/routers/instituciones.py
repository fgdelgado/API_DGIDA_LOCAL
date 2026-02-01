from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import List, Optional

# DynamoDB (resource, NO client)
from database import get_dynamodb_resource

# Modelos Pydantic
from models.institucion import (
    InstitucionCreate,
    InstitucionUpdate,
    InstitucionResponse,
    InstitucionListItem,
)

# Utilidad para generar IDs con prefijo (INST-xxxx)
from utils.id_generator import generate_id

# --------------------------------------------------
# Router de FastAPI para Instituciones
# --------------------------------------------------
router = APIRouter(
    prefix="/instituciones",
    tags=["Instituciones"]
)

# --------------------------------------------------
# Conexión a DynamoDB (resource)
# --------------------------------------------------
dynamodb = get_dynamodb_resource()

# Nombre de la tabla DynamoDB
TABLE_NAME = "api_data"

# Referencia a la tabla
table = dynamodb.Table(TABLE_NAME)

# --------------------------------------------------
# Crear institución
# POST /instituciones
# --------------------------------------------------
@router.post("", response_model=InstitucionResponse)
def crear_institucion(data: InstitucionCreate):
    # Fecha actual en formato ISO 8601
    now = datetime.utcnow().isoformat()

    # Generar ID de institución (ej: INST-abc123)
    id_institucion = generate_id("INST-")

    # Item que se guardará en DynamoDB
    item = {
        # Claves primarias
        "PK": f"INSTITUCION#{id_institucion}",  # Partition Key
        "SK": "METADATA",                      # Sort Key

        # Datos propios de la institución
        "id_institucion": id_institucion,
        **data.model_dump(),

        # Campos de control
        "habil": True,
        "fecha_creacion": now,
        "fecha_actualizacion": now,
    }

    # Guardar en DynamoDB
    table.put_item(Item=item)

    return item

# --------------------------------------------------
# Obtener institución por ID
# GET /instituciones/{id}
# --------------------------------------------------
@router.get("/{id_institucion}", response_model=InstitucionResponse)
def obtener_institucion(id_institucion: str):
    response = table.get_item(
        Key={
            "PK": f"INSTITUCION#{id_institucion}",
            "SK": "METADATA",
        }
    )

    # Si no existe, error 404
    if "Item" not in response:
        raise HTTPException(
            status_code=404,
            detail="Institución no encontrada"
        )

    return response["Item"]

# --------------------------------------------------
# Listar instituciones
# GET /instituciones?habil=true|false
# --------------------------------------------------
@router.get("", response_model=List[InstitucionListItem])
def listar_instituciones(habil: Optional[bool] = Query(None)):
    # Scan completo (válido para pruebas; luego se optimiza)
    response = table.scan()
    items = response.get("Items", [])

    instituciones = []

    for item in items:
        # Aseguramos que sea una institución
        if item.get("SK") != "METADATA":
            continue

        # Filtrar por habil si viene en la query
        if habil is not None and item.get("habil") != habil:
            continue

        # Devolver solo id y nombre
        instituciones.append({
            "id_institucion": item["id_institucion"],
            "nombre": item["nombre"],
        })

    return instituciones

# --------------------------------------------------
# Actualizar institución (parcial)
# PATCH /instituciones/{id}
# --------------------------------------------------
@router.patch("/{id_institucion}", response_model=InstitucionResponse)
def actualizar_institucion(id_institucion: str, data: InstitucionUpdate):
    now = datetime.utcnow().isoformat()

    update_expression = []
    expression_values = {}

    # Campos dinámicos
    for field, value in data.model_dump(exclude_none=True).items():
        update_expression.append(f"{field} = :{field}")
        expression_values[f":{field}"] = value

    if not update_expression:
        raise HTTPException(
            status_code=400,
            detail="No hay campos para actualizar"
        )

    # Fecha de actualización
    update_expression.append("fecha_actualizacion = :fecha_actualizacion")
    expression_values[":fecha_actualizacion"] = now

    response = table.update_item(
        Key={
            "PK": f"INSTITUCION#{id_institucion}",
            "SK": "METADATA",
        },
        UpdateExpression="SET " + ", ".join(update_expression),
        ExpressionAttributeValues=expression_values,
        ReturnValues="ALL_NEW",
    )

    return response["Attributes"]

# --------------------------------------------------
# Habilitar institución
# PATCH /instituciones/{id}/habilitar
# --------------------------------------------------
@router.patch("/{id_institucion}/habilitar")
def habilitar_institucion(id_institucion: str):
    now = datetime.utcnow().isoformat()

    table.update_item(
        Key={
            "PK": f"INSTITUCION#{id_institucion}",
            "SK": "METADATA",
        },
        UpdateExpression=(
            "SET habil = :habil, "
            "fecha_actualizacion = :fecha"
        ),
        ExpressionAttributeValues={
            ":habil": True,
            ":fecha": now,
        },
    )

    return {
        "message": "Institución activada correctamente"
    }



# --------------------------------------------------
# Eliminar institución (delete lógico)
# DELETE /instituciones/{id}
# --------------------------------------------------
@router.delete("/{id_institucion}")
def eliminar_institucion(id_institucion: str):
    now = datetime.utcnow().isoformat()

    table.update_item(
        Key={
            "PK": f"INSTITUCION#{id_institucion}",
            "SK": "METADATA",
        },
        UpdateExpression=(
            "SET habil = :habil, "
            "fecha_actualizacion = :fecha"
        ),
        ExpressionAttributeValues={
            ":habil": False,
            ":fecha": now,
        },
    )

    return {
        "message": "Institución desactivada correctamente"
    }
