from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

# Modelo para CREAR una institución
# Define qué campos puede enviar el cliente
class InstitucionCreate(BaseModel):
    nombre: str
    departamento_sede: str
    municipio_sede: str
    telefono: str = Field(
        pattern=r'^\d{4}-\d{4}$',
        description="Formato requerido: 5555-5555"
    )
    correo: EmailStr
    
    # Validador para evitar solo espacios
    @field_validator("nombre", "departamento_sede", "municipio_sede")
    @classmethod
    def no_solo_espacios(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("No puede estar vacío o contener solo espacios.")
        return value.strip()

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

    @field_validator("nombre", "departamento_sede", "municipio_sede")
    @classmethod
    def no_solo_espacios(cls, value: Optional[str]):
        if value is None:
            return value  # Si no viene en el body, no validar

        if not value.strip():
            raise ValueError("No puede estar vacío o contener solo espacios.")

        return value.strip()

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

