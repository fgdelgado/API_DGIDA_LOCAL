import uuid

# Genera un ID único con un prefijo específico
# Ejemplo: INST-A93F21C8
def generate_id(prefix: str) -> str:
    # uuid4 genera un identificador único aleatorio
    # .hex lo convierte a string sin guiones
    # [:8] lo hace más corto y legible
    return f"{prefix}{uuid.uuid4().hex[:8]}"
