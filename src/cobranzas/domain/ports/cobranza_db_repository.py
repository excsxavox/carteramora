from typing import List, Protocol

from cobranzas.domain.models.credito import Credito


class CobranzaDbRepositoryPort(Protocol):
    """Puerto de salida: persiste cartera en mora en BD_Cobranza."""

    def guardar_creditos_mora(self, creditos: List[Credito]) -> int:
        """Inserta o actualiza deudores, deudas, asesores y asignaciones."""
