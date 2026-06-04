from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from cobranzas.domain.models.credito import Credito


@dataclass
class ProcesoContext:
    """Estado compartido que recorre la cadena de responsabilidad."""

    dias_mora_minimo: int
    archivo_morosidad: Path = Path(".")
    archivo_cartera: Path = Path(".")
    archivo_detalle_morosidad: Path = Path(".")
    archivo_detalle_mora: Path = Path(".")
    creditos: List[Credito] = field(default_factory=list)
    creditos_morosidad: List[Credito] = field(default_factory=list)
    total_cartera_leidas: int = 0
    total_enriquecidos: int = 0
    creditos_mora: List[Credito] = field(default_factory=list)
    columnas_morosidad: tuple[str, ...] = ()
    columnas_cartera: tuple[str, ...] = ()
    columnas_mora: tuple[str, ...] = ()
    reporte: Dict[str, Any] = field(default_factory=dict)
    persistir_en_bd: bool = False
    database_url: str = ""
    registros_persistidos_bd: int = 0
