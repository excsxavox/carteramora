from typing import List, Protocol

from cobranzas.domain.models.credito import Credito


class CobranzaDbRepositoryPort(Protocol):
    """Puerto de salida: persiste cartera en mora en BD_Cobranza."""

    def guardar_creditos_mora(self, creditos: List[Credito]) -> int:
        """
        Persiste el lote del día: borra deuda/asesores_deuda de la misma
        fecha_corte y vuelve a cargar; rollback si falla algún registro.
        """
