from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import uuid

from models.tramites import (
    TramiteCreate,
    TramiteUpdate,
    TramiteResponse,
    TramiteListItem
)

from database import get_dynamodb_resource


router = APIRouter(
    prefix="/tramites",
    tags=["Trámites"]
)

dynamodb = get_dynamodb_resource()

# Nombre de la tabla DynamoDB
TABLE_NAME = "api_data"

# Referencia a la tabla
table = dynamodb.Table(TABLE_NAME)


# --------------------------------------------------
# Crear trámite
# POST /tramites
# --------------------------------------------------
@router.post("", response_model=TramiteResponse)
def crear_tramite(data: TramiteCreate):
    now = datetime.utcnow().isoformat()
    id_tramite = f"TRM-{uuid.uuid4().hex[:8]}"

    item = {
        "PK": f"INSTITUCION#{data.id_institucion}",
        "SK": f"TRAMITE#{id_tramite}",

        "id_tramite": id_tramite,
        "id_institucion": data.id_institucion,

        "nombre_tramite": data.nombre_tramite,
        "descripcion": data.descripcion,
        "tipo_tramite": data.tipo_tramite,
        "canal_atencion": data.canal_atencion,
        "costo": data.costo,
        "requisitos": data.requisitos,

        "habil": data.habil,
        "fecha_creacion": now,
        "fecha_actualizacion": now,
    }

    table.put_item(Item=item)

    return item


# --------------------------------------------------
# Listar trámites
# GET /tramites
# --------------------------------------------------
@router.get("", response_model=List[TramiteListItem])
def listar_tramites(
    id_institucion: Optional[str] = Query(None),
    habil: Optional[bool] = Query(None),
):
    # Scan temporal (igual que instituciones)
    response = table.scan()
    items = response.get("Items", [])

    tramites = []

    for item in items:
        if not item.get("SK", "").startswith("TRAMITE#"):
            continue

        if id_institucion and item.get("id_institucion") != id_institucion:
            continue

        if habil is not None and item.get("habil") != habil:
            continue

        tramites.append({
            "id_tramite": item["id_tramite"],
            "nombre_tramite": item["nombre_tramite"],
            "habil": item["habil"],
        })

    return tramites


# --------------------------------------------------
# Obtener trámite
# GET /tramites/{id_tramite}
# --------------------------------------------------
@router.get("/{id_tramite}", response_model=TramiteResponse)
def obtener_tramite(id_tramite: str):
    response = table.scan()
    items = response.get("Items", [])

    for item in items:
        if item.get("id_tramite") == id_tramite:
            return item

    raise HTTPException(status_code=404, detail="Trámite no encontrado")


# --------------------------------------------------
# Actualizar trámite
# PATCH /tramites/{id_tramite}
# --------------------------------------------------
@router.patch("/{id_tramite}", response_model=TramiteResponse)
def actualizar_tramite(id_tramite: str, data: TramiteUpdate):
    now = datetime.utcnow().isoformat()

    # Buscar primero (temporal)
    response = table.scan()
    items = response.get("Items", [])

    tramite = next(
        (item for item in items if item.get("id_tramite") == id_tramite),
        None
    )

    if not tramite:
        raise HTTPException(status_code=404, detail="Trámite no encontrado")

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

    # Construcción segura del update
    update_kwargs = {
        "Key": {
            "PK": tramite["PK"],
            "SK": tramite["SK"],
        },
        "UpdateExpression": "SET " + ", ".join(update_expression),
        "ExpressionAttributeValues": expression_values,
        "ReturnValues": "ALL_NEW",
    }

    # SOLO si se usó 'habil'
    if expression_names:
        update_kwargs["ExpressionAttributeNames"] = expression_names

    response = table.update_item(**update_kwargs)

    return response["Attributes"]


# --------------------------------------------------
# Deshabilitar trámite
# DELETE /tramites/{id_tramite}
# --------------------------------------------------
@router.delete("/{id_tramite}")
def deshabilitar_tramite(id_tramite: str):
    now = datetime.utcnow().isoformat()

    response = table.scan()
    items = response.get("Items", [])

    tramite = next(
        (item for item in items if item.get("id_tramite") == id_tramite),
        None
    )

    if not tramite:
        raise HTTPException(status_code=404, detail="Trámite no encontrado")

    table.update_item(
        Key={
            "PK": tramite["PK"],
            "SK": tramite["SK"],
        },
        UpdateExpression=(
            "SET #habil = :habil, "
            "fecha_actualizacion = :fecha"
        ),
        ExpressionAttributeNames={
            "#habil": "habil"
        },
        ExpressionAttributeValues={
            ":habil": False,
            ":fecha": now,
        },
    )

    return {"message": "Trámite deshabilitado correctamente"}


# --------------------------------------------------
# Habilitar trámite
# PATCH /tramites/{id_tramite}/habilitar
# --------------------------------------------------
@router.patch("/{id_tramite}/habilitar")
def habilitar_tramite(id_tramite: str):
    now = datetime.utcnow().isoformat()

    response = table.scan()
    items = response.get("Items", [])

    tramite = next(
        (item for item in items if item.get("id_tramite") == id_tramite),
        None
    )

    if not tramite:
        raise HTTPException(status_code=404, detail="Trámite no encontrado")

    table.update_item(
        Key={
            "PK": tramite["PK"],
            "SK": tramite["SK"],
        },
        UpdateExpression=(
            "SET #habil = :habil, "
            "fecha_actualizacion = :fecha"
        ),
        ExpressionAttributeNames={
            "#habil": "habil"
        },
        ExpressionAttributeValues={
            ":habil": True,
            ":fecha": now,
        },
    )

    return {"message": "Trámite habilitado correctamente"}
