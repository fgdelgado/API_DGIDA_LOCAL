from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# Modelo para CREAR una institución
# Define qué campos puede enviar el cliente
class InstitucionCreate(BaseModel):
    nombre: str
    departamento_sede: str
    municipio_sede: str
    telefono: Optional[str] = Field(
        None,
        pattern=r'^\d{4}-\d{4}$',
        description="Formato requerido: 5555-5555"
    )
    correo: EmailStr

# Modelo para ACTUALIZAR una institución
# Todos los campos son opcionales (PATCH)
class InstitucionUpdate(BaseModel):
    nombre: Optional[str] = None
    departamento_sede: Optional[str] = None
    municipio_sede: Optional[str] = None
    telefono: Optional[str] = Field(
        None,
        pattern=r'^\d{4}-\d{4}$',
        description="Formato requerido: 5555-5555"
    )
    correo: Optional[EmailStr] = None

# Modelo de RESPUESTA completa
# Define lo que la API devuelve al cliente
class InstitucionResponse(BaseModel):
    id_institucion: str
    nombre: str
    departamento_sede: str
    municipio_sede: str
    telefono: str
    correo: str
    habil: bool
    fecha_creacion: str
    fecha_actualizacion: str

# Modelo para LISTADOS
# Solo id y nombre (optimiza respuestas)
class InstitucionListItem(BaseModel):
    id_institucion: str
    nombre: str
