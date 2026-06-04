from dataclasses import dataclass, field
from typing import List


@dataclass
class SincronizacionAsesoresResult:
    total_leidos: int = 0
    filas_excel: int = 0
    duplicados_excel_omitidos: int = 0
    creados: int = 0
    actualizados: int = 0
    sin_cambios: int = 0
    omitidos: int = 0
    advertencias: List[str] = field(default_factory=list)
    errores: List[str] = field(default_factory=list)
