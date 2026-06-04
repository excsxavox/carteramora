from abc import ABC, abstractmethod
from typing import List

from cobranzas.domain.models.asesor_registro import AsesorRegistro
from cobranzas.domain.models.sincronizacion_asesores_result import (
    SincronizacionAsesoresResult,
)


class AsesorSyncRepositoryPort(ABC):
    @abstractmethod
    def sincronizar(self, registros: List[AsesorRegistro]) -> SincronizacionAsesoresResult:
        """Inserta o actualiza asesores por cédula."""
