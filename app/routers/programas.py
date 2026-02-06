from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import uuid

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
table = dynamodb.Table("api_data")

#Crear programa
@router.post("", response_model=ProgramaResponse)
def crear_programa(data: ProgramaCreate):
    now = datetime.utcnow().isoformat()
    id_programa = f"PRG-{uuid.uuid4().hex[:8]}"

    item = {
        "PK": f"INSTITUCION#{data.id_institucion}",
        "SK": f"PROGRAMA#{id_programa}",

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

#Listar programas (por institución)
@router.get("", response_model=List[ProgramaListItem])
def listar_programas(
    id_institucion: Optional[str] = Query(None),
    habil: Optional[bool] = Query(None),
):
    response = table.scan()
    items = response.get("Items", [])

    programas = []

    for item in items:
        if not item.get("SK", "").startswith("PROGRAMA#"):
            continue

        if id_institucion and item.get("id_institucion") != id_institucion:
            continue

        if habil is not None and item.get("habil") != habil:
            continue

        programas.append({
            "id_programa": item["id_programa"],
            "nombre": item["nombre"],
            "habil": item["habil"],
        })

    return programas

#Obtener programa por id programa
@router.get("/{id_programa}", response_model=ProgramaResponse)
def obtener_programa(id_programa: str):
    response = table.scan()
    items = response.get("Items", [])

    for item in items:
        if item.get("id_programa") == id_programa:
            return item

    raise HTTPException(status_code=404, detail="Programa no encontrado")

#actualizar programa
@router.patch("/{id_programa}", response_model=ProgramaResponse)
def actualizar_programa(id_programa: str, data: ProgramaUpdate):
    now = datetime.utcnow().isoformat()

    response = table.scan()
    items = response.get("Items", [])

    programa = next(
        (item for item in items if item.get("id_programa") == id_programa),
        None
    )

    if not programa:
        raise HTTPException(status_code=404, detail="Programa no encontrado")

    update_expression = []
    expression_values = {}

    for field, value in data.model_dump(exclude_none=True).items():
        update_expression.append(f"{field} = :{field}")
        expression_values[f":{field}"] = value

    if not update_expression:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

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

#seshabilitar programa delete logico
@router.delete("/{id_programa}")
def deshabilitar_programa(id_programa: str):
    now = datetime.utcnow().isoformat()

    response = table.scan()
    items = response.get("Items", [])

    programa = next(
        (item for item in items if item.get("id_programa") == id_programa),
        None
    )

    if not programa:
        raise HTTPException(status_code=404, detail="Programa no encontrado")

    table.update_item(
        Key={
            "PK": programa["PK"],
            "SK": programa["SK"],
        },
        UpdateExpression="SET habil = :habil, fecha_actualizacion = :fecha",
        ExpressionAttributeValues={
            ":habil": False,
            ":fecha": now,
        },
    )

    return {"message": "Programa deshabilitado correctamente"}

#habilitar programa
@router.patch("/{id_programa}/habilitar")
def habilitar_programa(id_programa: str):
    now = datetime.utcnow().isoformat()

    response = table.scan()
    items = response.get("Items", [])

    programa = next(
        (item for item in items if item.get("id_programa") == id_programa),
        None
    )

    if not programa:
        raise HTTPException(status_code=404, detail="Programa no encontrado")

    table.update_item(
        Key={
            "PK": programa["PK"],
            "SK": programa["SK"],
        },
        UpdateExpression="SET habil = :habil, fecha_actualizacion = :fecha",
        ExpressionAttributeValues={
            ":habil": True,
            ":fecha": now,
        },
    )

    return {"message": "Programa habilitado correctamente"}
