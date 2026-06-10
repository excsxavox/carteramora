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
        Reemplaza filas del mismo fecha_proceso y agrega el lote.
        Retorna cantidad de filas escritas.
        """
