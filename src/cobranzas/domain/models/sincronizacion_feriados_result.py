from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SincronizacionFeriadosResult:
    archivo_excel: Optional[str] = None
    registros_excel: int = 0
    dias_insertados: int = 0
    dias_activados: int = 0
    dias_desactivados: int = 0
    omitidos_sin_excel: bool = False
    advertencias: List[str] = field(default_factory=list)
    errores: List[str] = field(default_factory=list)
