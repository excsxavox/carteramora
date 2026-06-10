from datetime import date
from pathlib import Path
from typing import Optional

from cobranzas.domain.models.credito import Credito
from cobranzas.domain.ports.cartera_repository import CarteraRepositoryPort
from cobranzas.infrastructure.adapters.te_detallado_cartera_parser import (
    leer_te_detallado_cartera,
)


class TsvCarteraRepository(CarteraRepositoryPort):
    """Adaptador: lee TE detallado de cartera consolidado (TAB)."""

    def __init__(
        self, file_path: Path, fecha_corte: Optional[date] = None
    ) -> None:
        self._file_path = file_path
        self._fecha_corte = fecha_corte

    def obtener_creditos(self) -> list[Credito]:
        _, _, creditos = leer_te_detallado_cartera(
            self._file_path, fecha_corte_override=self._fecha_corte
        )
        return creditos
