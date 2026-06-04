from abc import ABC, abstractmethod
from pathlib import Path

from cobranzas.domain.models.lote_carga import LoteCargaResult


class StagingRepositoryPort(ABC):
    """Carga archivos .lis limpios en tablas temporales de BD."""

    @abstractmethod
    def cargar_archivos_limpios(
        self,
        archivo_morosidad: Path,
        archivo_mora: Path,
    ) -> LoteCargaResult:
        """Crea lote, registra columnas y carga filas de ambos archivos."""
