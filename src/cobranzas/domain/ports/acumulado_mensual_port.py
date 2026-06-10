from abc import ABC, abstractmethod
from datetime import date
from typing import List

from cobranzas.domain.models.fila_acumulado_mensual import FilaAcumuladoMensual


class AcumuladoMensualPort(ABC):
    @abstractmethod
    def filas_por_fecha_corte(self, fecha_corte: date) -> List[FilaAcumuladoMensual]:
        """Deuda + asesores_deuda del lote persistido en la fecha indicada."""
