from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errores = []

    for error in exc.errors():
        campo = error["loc"][-1]
        tipo_error = error["type"]

        if tipo_error == "string_too_short":
            mensaje = f"El campo '{campo}' no puede estar vacío."

        elif tipo_error == "missing":
            mensaje = f"El campo '{campo}' es obligatorio."

        elif tipo_error == "string_pattern_mismatch" and campo == "telefono":
            mensaje = "El teléfono debe tener el formato 5555-5555."

        elif campo == "correo":
            mensaje = "El correo electrónico no tiene un formato válido."

        elif tipo_error == "value_error":
            mensaje = error["msg"]

        else:
            mensaje = f"Error de validación en el campo '{campo}'."

        errores.append({
            "campo": campo,
            "mensaje": mensaje
        })

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "message": "Error en los datos enviados.",
            "details": errores
        },
    )