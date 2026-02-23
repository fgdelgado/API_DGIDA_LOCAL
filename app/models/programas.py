from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class ProgramaBase(BaseModel):
    id_institucion: str
    nombre: str
    descripcion: Optional[str] = None
    habil: bool

    @field_validator("id_institucion", "nombre", "descripcion")
    @classmethod
    def no_solo_espacios(cls, value: Optional[str]):
        if value is None:
            return value  # Si no viene en el body, no validar

        if not value.strip():
            raise ValueError("No puede estar vacío o contener solo espacios.")

        return value.strip()

class ProgramaCreate(ProgramaBase):
    pass


class ProgramaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

    @field_validator("nombre", "descripcion")
    @classmethod
    def no_solo_espacios(cls, value: Optional[str]):
        if value is None:
            return value  # Si no viene en el body, no validar

        if not value.strip():
            raise ValueError("No puede estar vacío o contener solo espacios.")

        return value.strip()

class ProgramaResponse(ProgramaBase):
    id_programa: str
    fecha_creacion: str
    fecha_actualizacion: str


class ProgramaListItem(BaseModel):
    id_programa: str
    nombre: str
    habil: bool
