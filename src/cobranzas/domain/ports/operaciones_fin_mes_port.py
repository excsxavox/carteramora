from datetime import date
from typing import Protocol, Set


class OperacionesFinMesPort(Protocol):
    """Puerto de salida: consulta operaciones marcadas como fin de mes."""

    def operaciones_fin_de_mes(self, antes_de: date) -> Set[str]:
        """
        Números de operación capturados en un cierre de fin de mes
        (estado FIN_DE_MES en asesores_deuda) con fecha_corte anterior a
        ``antes_de``. Se usan para excluirlas del proceso del día siguiente.
        """
