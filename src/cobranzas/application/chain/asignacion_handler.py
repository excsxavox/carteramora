import logging

from cobranzas.application.chain.handler import Handler
from cobranzas.application.chain.proceso_context import ProcesoContext
from cobranzas.domain.services.asignacion_cartera_service import AsignacionCarteraService

logger = logging.getLogger(__name__)


class AsignacionHandler(Handler):
    """Paso 4: asignación secuencial balanceada a asesores de cobranza."""

    def __init__(self, asignacion_service: AsignacionCarteraService) -> None:
        super().__init__()
        self._asignacion = asignacion_service

    def _procesar(self, contexto: ProcesoContext) -> ProcesoContext:
        if not contexto.usar_mora_temprana or not contexto.creditos:
            return contexto

        fecha_corte = contexto.creditos[0].fecha_corte
        creditos, filas = self._asignacion.asignar(
            contexto.creditos, fecha_corte, es_fin_de_mes=contexto.es_fin_de_mes
        )
        contexto.creditos = creditos
        contexto.asignaciones = filas
        logger.info("Asignación completada | filas=%s", len(filas))
        return contexto
