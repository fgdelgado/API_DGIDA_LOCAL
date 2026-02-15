from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import uuid

from boto3.dynamodb.conditions import Key

from models.programas import (
    ProgramaCreate,
    ProgramaUpdate,
    ProgramaResponse,
    ProgramaListItem
)

from database import get_dynamodb_resource

router = APIRouter(
    prefix="/programas",
    tags=["Programas"]
)

dynamodb = get_dynamodb_resource()
table = dynamodb.Table("api_data_nube")

# --------------------------------------------------
# Crear programa
# --------------------------------------------------
@router.post("", response_model=ProgramaResponse)
def crear_programa(data: ProgramaCreate):
    now = datetime.utcnow().isoformat()
    id_programa = f"PRG-{uuid.uuid4().hex[:8]}"

    item = {
        # PK principal (agrupado por institución)
        "PK": f"INSTITUCION#{data.id_institucion}",
        "SK": f"PROGRAMA#{id_programa}",

        # GSI para acceso directo por id_programa
        "GSI1PK": f"PROGRAMA#{id_programa}",
        "GSI1SK": "METADATA",

        # Datos
        "id_programa": id_programa,
        "id_institucion": data.id_institucion,
        "nombre": data.nombre,
        "descripcion": data.descripcion,
        "habil": data.habil,
        "fecha_creacion": now,
        "fecha_actualizacion": now,
    }

    table.put_item(Item=item)
    return item

# --------------------------------------------------
# Listar programas por institución (OPTIMIZADO)
# --------------------------------------------------
@router.get("", response_model=List[ProgramaListItem])
def listar_programas(
    id_institucion: str = Query(...),
    habil: Optional[bool] = Query(None),
):
    response = table.query(
        KeyConditionExpression=(
            Key("PK").eq(f"INSTITUCION#{id_institucion}") &
            Key("SK").begins_with("PROGRAMA#")
        )
    )

    items = response.get("Items", [])
    programas = []

    for item in items:
        if habil is not None and item.get("habil") != habil:
            continue

        programas.append({
            "id_programa": item["id_programa"],
            "nombre": item["nombre"],
            "habil": item["habil"],
        })

    return programas

# --------------------------------------------------
# Obtener programa por ID (GSI)
# --------------------------------------------------
@router.get("/{id_programa}", response_model=ProgramaResponse)
def obtener_programa(id_programa: str):
    response = table.query(
        IndexName="GSI1",
        KeyConditionExpression=Key("GSI1PK").eq(f"PROGRAMA#{id_programa}")
    )

    items = response.get("Items", [])
    if not items:
        raise HTTPException(status_code=404, detail="Programa no encontrado, verificar id programa ingresado")

    return items[0]

# --------------------------------------------------
# Actualizar programa
# --------------------------------------------------
@router.patch("/{id_programa}", response_model=ProgramaResponse)
def actualizar_programa(id_programa: str, data: ProgramaUpdate):
    now = datetime.utcnow().isoformat()

    response = table.query(
        IndexName="GSI1",
        KeyConditionExpression=Key("GSI1PK").eq(f"PROGRAMA#{id_programa}")
    )

    items = response.get("Items", [])
    if not items:
        raise HTTPException(status_code=404, detail="Programa no encontrado, verificar id programa ingresado")

    programa = items[0]

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
            "PK": programa["PK"],
            "SK": programa["SK"],
        },
        UpdateExpression="SET " + ", ".join(update_expression),
        ExpressionAttributeValues=expression_values,
        ReturnValues="ALL_NEW",
    )

    return response["Attributes"]

# --------------------------------------------------
# Deshabilitar programa (delete lógico)
# --------------------------------------------------
@router.delete("/{id_programa}")
def deshabilitar_programa(id_programa: str):
    return _set_habil_programa(id_programa, False)

# --------------------------------------------------
# Habilitar programa
# --------------------------------------------------
@router.patch("/{id_programa}/habilitar")
def habilitar_programa(id_programa: str):
    return _set_habil_programa(id_programa, True)

# --------------------------------------------------
# Función interna reutilizable
# --------------------------------------------------
def _set_habil_programa(id_programa: str, habil: bool):
    now = datetime.utcnow().isoformat()

    response = table.query(
        IndexName="GSI1",
        KeyConditionExpression=Key("GSI1PK").eq(f"PROGRAMA#{id_programa}")
    )

    items = response.get("Items", [])
    if not items:
        raise HTTPException(status_code=404, detail="Programa no encontrado, verificar id_programa ingresado")

    programa = items[0]

    table.update_item(
        Key={
            "PK": programa["PK"],
            "SK": programa["SK"],
        },
        UpdateExpression="SET habil = :habil, fecha_actualizacion = :fecha",
        ExpressionAttributeValues={
            ":habil": habil,
            ":fecha": now,
        },
    )

    return {
        "message": "Programa habilitado correctamente"
        if habil else
        "Programa deshabilitado correctamente"
    }
