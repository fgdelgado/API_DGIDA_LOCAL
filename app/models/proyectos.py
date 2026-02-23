from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class ProyectoBase(BaseModel):
    id_institucion: str
    nombre: str
    descripcion: Optional[str] = None
    estado_proyecto: str
    habil: bool = True

    @field_validator("id_institucion", "nombre", "descripcion", "estado_proyecto")
    @classmethod
    def no_solo_espacios(cls, value: Optional[str]):
        if value is None:
            return value  # Si no viene en el body, no validar

        if not value.strip():
            raise ValueError("No puede estar vacío o contener solo espacios.")

        return value.strip()

class ProyectoCreate(ProyectoBase):
    pass

class ProyectoListItem(BaseModel):
    id_proyecto: str
    nombre: str
    estado_proyecto: str
    habil: bool

class ProyectoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    estado_proyecto: Optional[str] = None

    @field_validator("nombre", "descripcion", "estado_proyecto")
    @classmethod
    def no_solo_espacios(cls, value: Optional[str]):
        if value is None:
            return value  # Si no viene en el body, no validar

        if not value.strip():
            raise ValueError("No puede estar vacío o contener solo espacios.")

        return value.strip()

class ProyectoResponse(ProyectoBase):
    id_proyecto: str
    fecha_creacion: str
    fecha_actualizacion: Optional[str] = None
