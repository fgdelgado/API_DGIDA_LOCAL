from pydantic import BaseModel, Field, field_validator
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

    # Validación SOLO para strings
    @field_validator("id_institucion", "nombre_tramite", "descripcion", "tipo_tramite", "canal_atencion", "costo")
    @classmethod
    def no_solo_espacios(cls, value: str):
        if not value.strip():
            raise ValueError("No puede estar vacío o contener solo espacios.")
        return value.strip()

    # Validación específica para lista
    @field_validator("requisitos")
    @classmethod
    def validar_requisitos(cls, value: List[str]):
        if not value:
            raise ValueError("Debe incluir al menos un requisito.")

        requisitos_limpios = []
        for requisito in value:
            if not requisito.strip():
                raise ValueError("Los requisitos no pueden estar vacíos.")
            requisitos_limpios.append(requisito.strip())

        return requisitos_limpios

# ------------------------------
# Create
# ------------------------------
class TramiteCreate(TramiteBase):
    pass


# ------------------------------
# Update (todos opcionales)
# ------------------------------
class TramiteUpdate(BaseModel):
    nombre_tramite: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_tramite: Optional[str] = None
    canal_atencion: Optional[str] = None
    costo: Optional[str] = None
    requisitos: Optional[List[str]] = None

    # Validación para strings opcionales
    @field_validator("nombre_tramite","descripcion","tipo_tramite","canal_atencion","costo")
    @classmethod
    def no_solo_espacios(cls, value: Optional[str]):
        if value is None:
            return value  # No se envió en el body

        if not value.strip():
            raise ValueError("No puede estar vacío o contener solo espacios.")

        return value.strip()

    # Validación para lista opcional
    @field_validator("requisitos")
    @classmethod
    def validar_requisitos(cls, value: Optional[List[str]]):
        if value is None:
            return value  # No se envió en el body

        if not value:
            raise ValueError("La lista de requisitos no puede estar vacía.")

        requisitos_limpios = []
        for requisito in value:
            if not requisito.strip():
                raise ValueError("Los requisitos no pueden estar vacíos.")
            requisitos_limpios.append(requisito.strip())

        return requisitos_limpios

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
