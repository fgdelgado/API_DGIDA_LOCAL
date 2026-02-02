from pydantic import BaseModel, Field
from typing import List, Optional


# ------------------------------
# Base
# ------------------------------
class TramiteBase(BaseModel):
    id_institucion: str
    nombre_tramite: str = Field(..., min_length=3)
    descripcion: str
    tipo_tramite: str
    canal_atencion: str
    costo: str
    requisitos: List[str]
    habil: bool


# ------------------------------
# Create
# ------------------------------
class TramiteCreate(TramiteBase):
    pass


# ------------------------------
# Update (todos opcionales)
# ------------------------------
class TramiteUpdate(BaseModel):
    nombre_tramite: Optional[str]
    descripcion: Optional[str]
    tipo_tramite: Optional[str]
    canal_atencion: Optional[str]
    costo: Optional[str]
    requisitos: Optional[List[str]]


# ------------------------------
# Response
# ------------------------------
class TramiteResponse(TramiteBase):
    id_tramite: str
    id_institucion: str
    fecha_creacion: str
    fecha_actualizacion: str


# ------------------------------
# List
# ------------------------------
class TramiteListItem(BaseModel):
    id_tramite: str
    nombre_tramite: str
    habil: bool
