from pathlib import Path

from cartera_mora.domain.models.credito import Credito
from cartera_mora.domain.ports.cartera_repository import CarteraRepositoryPort
from cartera_mora.infrastructure.adapters.te_detallado_cartera_parser import (
    leer_te_detallado_cartera,
)


class TsvCarteraRepository(CarteraRepositoryPort):
    """Adaptador: lee TE detallado de cartera consolidado (TAB)."""

    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path

    def obtener_creditos(self) -> list[Credito]:
        _, creditos = leer_te_detallado_cartera(self._file_path)
        return creditos
