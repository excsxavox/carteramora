from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from cobranzas.domain.models.asesor_registro import AsesorRegistro


class AsesorExcelRepositoryPort(ABC):
    @abstractmethod
    def leer_asesores(self, archivo_excel: Path) -> List[AsesorRegistro]:
        """Lee filas de asesores desde la primera hoja del Excel."""
