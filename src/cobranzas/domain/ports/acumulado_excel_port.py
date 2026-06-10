from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path
from typing import List

from cobranzas.domain.models.fila_acumulado_mensual import FilaAcumuladoMensual


class AcumuladoExcelPort(ABC):
    @abstractmethod
    def anexar_lote(
        self,
        archivo: Path,
        fecha_corte: date,
        filas: List[FilaAcumuladoMensual],
    ) -> int:
        """
        Actualiza o agrega por OPERACION (una fila por operación en el mes).
        Retorna cantidad de filas del lote procesado.
        """
