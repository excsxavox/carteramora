from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AsesorRegistro:
    """Fila de asesor leída desde Excel (antes de persistir)."""

    cedula: str
    nombre: str
    numero_telefono: str = ""
    email: str = ""
    activo: bool = True
