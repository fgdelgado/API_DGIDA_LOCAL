from fastapi import APIRouter, HTTPException
from datetime import datetime
from uuid import uuid4

from database import get_dynamodb_resource
from models.proyecto import (
    ProyectoCreate,
    ProyectoUpdate,
    ProyectoResponse
)

router = APIRouter(
    prefix="/proyectos",
    tags=["Proyectos"]
)

dynamodb = get_dynamodb_resource()
table = dynamodb.Table("api_data")

#Crear proyecto (POST)
@router.post("/", response_model=ProyectoResponse)
def crear_proyecto(data: ProyectoCreate):
    now = datetime.utcnow().isoformat()
    id_proyecto = str(uuid4())

    item = {
        "PK": f"PROYECTO#{id_proyecto}",
        "SK": "METADATA",
        "id_proyecto": id_proyecto,
        "id_institucion": data.id_institucion,
        "nombre": data.nombre,
        "descripcion": data.descripcion,
        "estado_proyecto": data.estado_proyecto,
        "habil": data.habil,
        "fecha_creacion": now,
        "fecha_actualizacion": None,
    }

    table.put_item(Item=item)
    return item

#Obtener proyecto por ID (GET)
@router.get("/{id_proyecto}", response_model=ProyectoResponse)
def obtener_proyecto(id_proyecto: str):
    response = table.get_item(
        Key={
            "PK": f"PROYECTO#{id_proyecto}",
            "SK": "METADATA",
        }
    )

    item = response.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    return item

#Actualizar proyecto (PATCH)
@router.patch("/{id_proyecto}", response_model=ProyectoResponse)
def actualizar_proyecto(id_proyecto: str, data: ProyectoUpdate):
    now = datetime.utcnow().isoformat()

    update_expression = []
    expression_values = {}
    expression_names = {}

    for field, value in data.model_dump(exclude_none=True).items():
        if field == "habil":
            update_expression.append("#habil = :habil")
            expression_names["#habil"] = "habil"
            expression_values[":habil"] = value
        else:
            update_expression.append(f"{field} = :{field}")
            expression_values[f":{field}"] = value

    if not update_expression:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

    update_expression.append("fecha_actualizacion = :fecha")
    expression_values[":fecha"] = now

    update_kwargs = {
        "Key": {
            "PK": f"PROYECTO#{id_proyecto}",
            "SK": "METADATA",
        },
        "UpdateExpression": "SET " + ", ".join(update_expression),
        "ExpressionAttributeValues": expression_values,
        "ReturnValues": "ALL_NEW",
    }

    if expression_names:
        update_kwargs["ExpressionAttributeNames"] = expression_names

    response = table.update_item(**update_kwargs)
    return response["Attributes"]

#Eliminar proyecto (DELETE lógico)
@router.delete("/{id_proyecto}")
def eliminar_proyecto(id_proyecto: str):
    now = datetime.utcnow().isoformat()

    table.update_item(
        Key={
            "PK": f"PROYECTO#{id_proyecto}",
            "SK": "METADATA",
        },
        UpdateExpression="SET #habil = :habil, fecha_actualizacion = :fecha",
        ExpressionAttributeNames={
            "#habil": "habil"
        },
        ExpressionAttributeValues={
            ":habil": False,
            ":fecha": now
        }
    )

    return {"message": "Proyecto deshabilitado correctamente"}

