from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LoteCargaResult:
    """Resultado del job de carga a tablas temporales."""

    id_lote: int
    filas_morosidad: int
    filas_mora: int
    columnas_morosidad: int
    columnas_mora: int
    archivo_morosidad: Path
    archivo_mora: Path
