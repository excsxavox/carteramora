from pathlib import Path

from cobranzas.domain.models.credito import Credito
from cobranzas.domain.ports.credito_repository import CreditoRepositoryPort
from cobranzas.infrastructure.adapters.tsv_file_io import leer_creditos_tsv


class TsvCreditoRepository(CreditoRepositoryPort):
    """Adaptador: lee créditos desde archivo 1 (separado por tabs)."""

    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path

    def obtener_creditos(self) -> list[Credito]:
        return leer_creditos_tsv(self._file_path)
