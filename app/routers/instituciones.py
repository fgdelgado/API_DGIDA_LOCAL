from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import List, Optional

from database import get_dynamodb_resource

from models.instituciones import (
    InstitucionCreate,
    InstitucionUpdate,
    InstitucionResponse,
    InstitucionListItem,
)

from utils.id_generator import generate_id
from boto3.dynamodb.conditions import Key

router = APIRouter(
    prefix="/instituciones",
    tags=["Instituciones"]
)

dynamodb = get_dynamodb_resource()
TABLE_NAME = "api_data_nube"
table = dynamodb.Table(TABLE_NAME)

# --------------------------------------------------
# Crear institución
# --------------------------------------------------
@router.post("", response_model=InstitucionResponse)
def crear_institucion(data: InstitucionCreate):
    now = datetime.utcnow().isoformat()
    id_institucion = generate_id("INST-")

    item = {
        # PK principal
        "PK": f"INSTITUCION#{id_institucion}",
        "SK": "METADATA",

        # GSI para listados
        "GSI1PK": "INSTITUCIONES",
        "GSI1SK": f"INSTITUCION#{id_institucion}",

        # Datos
        "id_institucion": id_institucion,
        **data.model_dump(),

        "habil": True,
        "fecha_creacion": now,
        "fecha_actualizacion": now,
    }

    table.put_item(Item=item)
    return item

# --------------------------------------------------
# Obtener institución por ID
# --------------------------------------------------
@router.get("/{id_institucion}", response_model=InstitucionResponse)
def obtener_institucion(id_institucion: str):
    response = table.get_item(
        Key={
            "PK": f"INSTITUCION#{id_institucion}",
            "SK": "METADATA",
        }
    )

    if "Item" not in response:
        raise HTTPException(status_code=404, detail="Institución no encontrada")

    return response["Item"]

# --------------------------------------------------
# Listar instituciones (OPTIMIZADO)
# --------------------------------------------------
@router.get("", response_model=List[InstitucionListItem])
def listar_instituciones(habil: Optional[bool] = Query(None)):
    response = table.query(
        IndexName="GSI1",
        KeyConditionExpression=Key("GSI1PK").eq("INSTITUCIONES")
    )

    items = response.get("Items", [])
    instituciones = []

    for item in items:
        if habil is not None and item.get("habil") != habil:
            continue

        instituciones.append({
            "id_institucion": item["id_institucion"],
            "nombre": item["nombre"],
        })

    return instituciones

# --------------------------------------------------
# Actualizar institución
# --------------------------------------------------
@router.patch("/{id_institucion}", response_model=InstitucionResponse)
def actualizar_institucion(id_institucion: str, data: InstitucionUpdate):
    now = datetime.utcnow().isoformat()

    update_expression = []
    expression_values = {}

    for field, value in data.model_dump(exclude_none=True).items():
        update_expression.append(f"{field} = :{field}")
        expression_values[f":{field}"] = value

    if not update_expression:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

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
# --------------------------------------------------
@router.patch("/{id_institucion}/habilitar")
def habilitar_institucion(id_institucion: str):
    now = datetime.utcnow().isoformat()

    table.update_item(
        Key={
            "PK": f"INSTITUCION#{id_institucion}",
            "SK": "METADATA",
        },
        UpdateExpression="SET habil = :habil, fecha_actualizacion = :fecha",
        ExpressionAttributeValues={
            ":habil": True,
            ":fecha": now,
        },
    )

    return {"message": "Institución activada correctamente"}

# --------------------------------------------------
# Eliminar institución (lógico)
# --------------------------------------------------
@router.delete("/{id_institucion}")
def eliminar_institucion(id_institucion: str):
    now = datetime.utcnow().isoformat()

    table.update_item(
        Key={
            "PK": f"INSTITUCION#{id_institucion}",
            "SK": "METADATA",
        },
        UpdateExpression="SET habil = :habil, fecha_actualizacion = :fecha",
        ExpressionAttributeValues={
            ":habil": False,
            ":fecha": now,
        },
    )

    return {"message": "Institución desactivada correctamente"}
