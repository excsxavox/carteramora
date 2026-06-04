from pathlib import Path

from cobranzas.domain.models.lote_carga import LoteCargaResult
from cobranzas.domain.ports.staging_repository import StagingRepositoryPort


class CargarStagingService:
    """Job 2: carga archivos limpios (.lis) a tablas temporales."""

    def __init__(self, repository: StagingRepositoryPort) -> None:
        self._repository = repository

    def ejecutar(
        self,
        archivo_morosidad: Path,
        archivo_mora: Path,
    ) -> LoteCargaResult:
        return self._repository.cargar_archivos_limpios(
            archivo_morosidad, archivo_mora
        )
