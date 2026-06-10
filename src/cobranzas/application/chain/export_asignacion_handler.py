import logging

from cobranzas.application.chain.handler import Handler
from cobranzas.application.chain.proceso_context import ProcesoContext
from cobranzas.domain.services.asignacion_calendario import debe_exportar_asignacion
from cobranzas.domain.services.exportar_asignacion_service import ExportarAsignacionService

logger = logging.getLogger(__name__)


class ExportAsignacionHandler(Handler):
    """Genera ASIGNACION.csv (entregable HU-GRC-01)."""

    def __init__(self, export_service: ExportarAsignacionService) -> None:
        super().__init__()
        self._export = export_service

    def _procesar(self, contexto: ProcesoContext) -> ProcesoContext:
        if contexto.creditos:
            fecha_corte = contexto.creditos[0].fecha_corte
            if not debe_exportar_asignacion(fecha_corte):
                logger.info(
                    "ASIGNACION.csv omitido | %s | último día del mes | solo historial",
                    fecha_corte.isoformat(),
                )
                return contexto

        ids_recblue = {
            c.id_credito: (c.id_credito_recblue or "").strip()
            for c in contexto.creditos_mora
            if (c.id_credito_recblue or "").strip()
        }
        self._export.exportar_csv(
            contexto.archivo_asignacion,
            contexto.asignaciones,
            ids_recblue_por_operacion=ids_recblue,
        )
        logger.info("Entregable: %s", contexto.archivo_asignacion)
        return contexto
