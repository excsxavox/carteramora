from cobranzas.domain.models.sincronizacion_feriados_result import (
    SincronizacionFeriadosResult,
)
from cobranzas.domain.services.sincronizar_feriados_service import (
    SincronizarFeriadosService,
)


class SincronizarFeriadosUseCase:
    def __init__(self, service: SincronizarFeriadosService) -> None:
        self._service = service

    def ejecutar(self) -> SincronizacionFeriadosResult:
        return self._service.ejecutar()
