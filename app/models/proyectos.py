from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProyectoBase(BaseModel):
    id_institucion: str
    nombre: str
    descripcion: Optional[str] = None
    estado_proyecto: str
    habil: bool = True


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
    habil: Optional[bool] = None


class ProyectoResponse(ProyectoBase):
    id_proyecto: str
    fecha_creacion: str
    fecha_actualizacion: Optional[str] = None
