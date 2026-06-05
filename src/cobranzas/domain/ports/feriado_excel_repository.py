from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from cobranzas.domain.models.feriado_rango import FeriadoRango


class FeriadoExcelRepositoryPort(ABC):
    @abstractmethod
    def buscar_archivo(self, directorio: Path, patron: str) -> Optional[Path]:
        """Devuelve el Excel más reciente que coincida con el patrón."""

    @abstractmethod
    def leer_feriados(self, archivo_excel: Path) -> List[FeriadoRango]:
        """Lee filas válidas del Excel de feriados."""
