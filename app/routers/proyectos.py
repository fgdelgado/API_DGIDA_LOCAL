from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from uuid import uuid4
from typing import List, Optional

from boto3.dynamodb.conditions import Key

from database import get_dynamodb_resource
from models.proyectos import (
    ProyectoCreate,
    ProyectoUpdate,
    ProyectoResponse,
    ProyectoListItem
)

router = APIRouter(
    prefix="/proyectos",
    tags=["Proyectos"]
)

dynamodb = get_dynamodb_resource()
table = dynamodb.Table("api_data_nube")

# --------------------------------------------------
# Crear proyecto
# POST /proyectos
# --------------------------------------------------
@router.post("", response_model=ProyectoResponse)
def crear_proyecto(data: ProyectoCreate):
    now = datetime.utcnow().isoformat()
    id_proyecto = f"PRY-{uuid4().hex[:8]}"

    item = {
        # PK principal (agrupado por institución)
        "PK": f"INSTITUCION#{data.id_institucion}",
        "SK": f"PROYECTO#{id_proyecto}",

        # GSI para acceso directo por id_proyecto
        "GSI1PK": f"PROYECTO#{id_proyecto}",
        "GSI1SK": "METADATA",

        # Datos
        "id_proyecto": id_proyecto,
        "id_institucion": data.id_institucion,
        "nombre": data.nombre,
        "descripcion": data.descripcion,
        "estado_proyecto": data.estado_proyecto,
        "habil": data.habil,
        "fecha_creacion": now,
        "fecha_actualizacion": now,
    }

    table.put_item(Item=item)
    return item

# --------------------------------------------------
# Listar proyectos por institución (OPTIMIZADO)
# GET /proyectos?id_institucion=...
# --------------------------------------------------
@router.get("", response_model=List[ProyectoListItem])
def listar_proyectos(
    id_institucion: str = Query(...),
    habil: Optional[bool] = Query(None),
):
    response = table.query(
        KeyConditionExpression=(
            Key("PK").eq(f"INSTITUCION#{id_institucion}") &
            Key("SK").begins_with("PROYECTO#")
        )
    )

    items = response.get("Items", [])
    proyectos = []

    for item in items:
        if habil is not None and item.get("habil") != habil:
            continue

        proyectos.append({
            "id_proyecto": item["id_proyecto"],
            "nombre": item["nombre"],
            "estado_proyecto": item["estado_proyecto"],
            "habil": item["habil"],
        })

    return proyectos

# --------------------------------------------------
# Obtener proyecto por ID (GSI)
# GET /proyectos/{id_proyecto}
# --------------------------------------------------
@router.get("/{id_proyecto}", response_model=ProyectoResponse)
def obtener_proyecto(id_proyecto: str):
    response = table.query(
        IndexName="GSI1",
        KeyConditionExpression=Key("GSI1PK").eq(f"PROYECTO#{id_proyecto}")
    )

    items = response.get("Items", [])
    if not items:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado, verificar id_proyecto ingresado")

    return items[0]

# --------------------------------------------------
# Actualizar proyecto
# PATCH /proyectos/{id_proyecto}
# --------------------------------------------------
@router.patch("/{id_proyecto}", response_model=ProyectoResponse)
def actualizar_proyecto(id_proyecto: str, data: ProyectoUpdate):
    now = datetime.utcnow().isoformat()

    response = table.query(
        IndexName="GSI1",
        KeyConditionExpression=Key("GSI1PK").eq(f"PROYECTO#{id_proyecto}")
    )

    items = response.get("Items", [])
    if not items:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado, verificar id_proyecto ingresado")

    proyecto = items[0]

    update_expression = []
    expression_values = {}

    for field, value in data.model_dump(exclude_none=True).items():
        update_expression.append(f"{field} = :{field}")
        expression_values[f":{field}"] = value

    if not update_expression:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar o no coinciden con los existentes")

    update_expression.append("fecha_actualizacion = :fecha")
    expression_values[":fecha"] = now

    response = table.update_item(
        Key={
            "PK": proyecto["PK"],
            "SK": proyecto["SK"],
        },
        UpdateExpression="SET " + ", ".join(update_expression),
        ExpressionAttributeValues=expression_values,
        ReturnValues="ALL_NEW",
    )

    return response["Attributes"]

# --------------------------------------------------
# Eliminar proyecto (delete lógico)
# --------------------------------------------------
@router.delete("/{id_proyecto}")
def eliminar_proyecto(id_proyecto: str):
    return _set_habil_proyecto(id_proyecto, False)

# --------------------------------------------------
# Habilitar proyecto
# --------------------------------------------------
@router.patch("/{id_proyecto}/habilitar")
def habilitar_proyecto(id_proyecto: str):
    return _set_habil_proyecto(id_proyecto, True)

# --------------------------------------------------
# Función interna reutilizable
# --------------------------------------------------
def _set_habil_proyecto(id_proyecto: str, habil: bool):
    now = datetime.utcnow().isoformat()

    response = table.query(
        IndexName="GSI1",
        KeyConditionExpression=Key("GSI1PK").eq(f"PROYECTO#{id_proyecto}")
    )

    items = response.get("Items", [])
    if not items:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado, verificar id_proyecto ingresado")

    proyecto = items[0]

    table.update_item(
        Key={
            "PK": proyecto["PK"],
            "SK": proyecto["SK"],
        },
        UpdateExpression="SET habil = :habil, fecha_actualizacion = :fecha",
        ExpressionAttributeValues={
            ":habil": habil,
            ":fecha": now,
        },
    )

    return {
        "message": "Proyecto habilitado correctamente"
        if habil else
        "Proyecto deshabilitado correctamente"
    }
