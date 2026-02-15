from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProgramaBase(BaseModel):
    id_institucion: str
    nombre: str
    descripcion: Optional[str] = None
    habil: bool


class ProgramaCreate(ProgramaBase):
    pass


class ProgramaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None


class ProgramaResponse(ProgramaBase):
    id_programa: str
    fecha_creacion: str
    fecha_actualizacion: str


class ProgramaListItem(BaseModel):
    id_programa: str
    nombre: str
    habil: bool
