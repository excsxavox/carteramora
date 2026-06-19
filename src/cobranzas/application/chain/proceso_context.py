from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from cobranzas.domain.models.asignacion_credito import AsignacionCredito
from cobranzas.domain.models.credito import Credito


@dataclass
class ProcesoContext:
    """Estado compartido que recorre la cadena de responsabilidad."""

    dias_mora_minimo: int
    usar_mora_temprana: bool = False
    mora_temprana_dias_min: int = 1
    mora_temprana_dias_max: int = 0
    es_fin_de_mes: bool = False
    estados_excluidos: tuple[str, ...] = ()
    tipos_oper_excluidos: tuple[str, ...] = ()
    archivo_morosidad: Path = Path(".")
    archivo_cartera: Path = Path(".")
    archivo_detalle_morosidad: Path = Path(".")
    archivo_detalle_mora: Path = Path(".")
    archivo_asignacion: Path = Path("destino/ASIGNACION.csv")
    archivo_acumulado_mensual: Optional[Path] = None
    archivo_acumulado_fin_mes: Optional[Path] = None
    archivo_recblue: Optional[Path] = None
    validar_recblue: bool = False
    mapa_recblue: Dict[str, str] = field(default_factory=dict)
    errores_recblue: List[str] = field(default_factory=list)
    creditos: List[Credito] = field(default_factory=list)
    creditos_morosidad: List[Credito] = field(default_factory=list)
    total_cartera_leidas: int = 0
    total_enriquecidos: int = 0
    creditos_mora: List[Credito] = field(default_factory=list)
    columnas_morosidad: tuple[str, ...] = ()
    columnas_cartera: tuple[str, ...] = ()
    columnas_mora: tuple[str, ...] = ()
    reporte: Dict[str, Any] = field(default_factory=dict)
    metricas_mora_temprana: Dict[str, Any] = field(default_factory=dict)
    asignaciones: List[AsignacionCredito] = field(default_factory=list)
    persistir_en_bd: bool = False
    database_url: str = ""
    registros_persistidos_bd: int = 0
