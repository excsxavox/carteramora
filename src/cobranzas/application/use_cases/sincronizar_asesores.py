from cobranzas.domain.models.sincronizacion_asesores_result import (
    SincronizacionAsesoresResult,
)
from cobranzas.domain.services.sincronizar_asesores_service import (
    SincronizarAsesoresService,
)
from cobranzas.infrastructure.config.settings import Settings


class SincronizarAsesoresUseCase:
    def __init__(self, service: SincronizarAsesoresService, settings: Settings) -> None:
        self._service = service
        self._settings = settings

    def ejecutar(self) -> SincronizacionAsesoresResult:
        return self._service.ejecutar(self._settings.archivo_excel_asesores)
