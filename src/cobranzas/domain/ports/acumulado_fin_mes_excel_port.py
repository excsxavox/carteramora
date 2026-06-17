from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path
from typing import List

from cobranzas.domain.models.fila_acumulado_fin_mes import FilaAcumuladoFinMes


class AcumuladoFinMesExcelPort(ABC):
    @abstractmethod
    def anexar_lote(
        self,
        archivo: Path,
        fecha_corte: date,
        filas: List[FilaAcumuladoFinMes],
    ) -> int:
        """Actualiza o agrega por numero_operacion. Retorna filas del lote."""
