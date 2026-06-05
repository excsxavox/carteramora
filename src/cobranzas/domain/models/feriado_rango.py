from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class FeriadoRango:
    """Rango de días feriados leído desde Excel."""

    descripcion: str
    fecha_inicio: date
    fecha_fin: date
