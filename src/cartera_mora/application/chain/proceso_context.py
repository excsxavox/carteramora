from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from cartera_mora.domain.models.credito import Credito


@dataclass
class ProcesoContext:
    """Estado compartido que recorre la cadena de responsabilidad."""

    dias_mora_minimo: int
    archivo_morosidad: Path = Path(".")
    archivo_cartera: Path = Path(".")
    archivo_reporte: Path = Path(".")
    archivo_lis: Path = Path(".")
    creditos: List[Credito] = field(default_factory=list)
    creditos_morosidad: List[Credito] = field(default_factory=list)
    total_cartera_leidas: int = 0
    total_enriquecidos: int = 0
    creditos_mora: List[Credito] = field(default_factory=list)
    reporte: Dict[str, Any] = field(default_factory=dict)
