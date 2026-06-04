from cobranzas.domain.models.lote_carga import LoteCargaResult
from cobranzas.domain.services.cargar_staging_service import CargarStagingService
from cobranzas.infrastructure.config.settings import Settings


class CargarStagingUseCase:
    def __init__(self, service: CargarStagingService, settings: Settings) -> None:
        self._service = service
        self._settings = settings

    def ejecutar(self) -> LoteCargaResult:
        return self._service.ejecutar(
            self._settings.archivo_salida_morosidad,
            self._settings.archivo_salida_mora,
        )
