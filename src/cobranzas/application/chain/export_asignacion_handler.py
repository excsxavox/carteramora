import logging

from cobranzas.application.chain.handler import Handler
from cobranzas.application.chain.proceso_context import ProcesoContext
from cobranzas.domain.services.exportar_asignacion_service import ExportarAsignacionService

logger = logging.getLogger(__name__)


class ExportAsignacionHandler(Handler):
    """Genera ASIGNACION.csv (entregable HU-GRC-01)."""

    def __init__(self, export_service: ExportarAsignacionService) -> None:
        super().__init__()
        self._export = export_service

    def _procesar(self, contexto: ProcesoContext) -> ProcesoContext:
        if not contexto.asignaciones:
            return contexto
        self._export.exportar_csv(contexto.archivo_asignacion, contexto.asignaciones)
        logger.info("Entregable: %s", contexto.archivo_asignacion)
        return contexto
