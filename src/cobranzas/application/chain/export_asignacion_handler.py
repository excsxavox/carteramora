import logging
from pathlib import Path
from typing import Optional

from cobranzas.application.chain.handler import Handler
from cobranzas.application.chain.proceso_context import ProcesoContext
from cobranzas.domain.ports.feriados_calendario_port import FeriadosCalendarioPort
from cobranzas.domain.services.asignacion_calendario import debe_exportar_asignacion
from cobranzas.domain.services.exportar_asignacion_service import ExportarAsignacionService
from cobranzas.infrastructure.config.entregables_mensuales import (
    ruta_asignacion_desde_fecha_archivo,
)

logger = logging.getLogger(__name__)


class ExportAsignacionHandler(Handler):
    """Genera ASIGNACION.csv (entregable HU-GRC-01)."""

    def __init__(
        self,
        export_service: ExportarAsignacionService,
        feriados_repository: Optional[FeriadosCalendarioPort] = None,
        directorio_destino: Optional[Path] = None,
    ) -> None:
        super().__init__()
        self._export = export_service
        self._feriados = feriados_repository
        self._directorio_destino = directorio_destino

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
        ruta = self._resolver_ruta_asignacion(contexto)
        contexto.archivo_asignacion = ruta
        self._export.exportar_csv(
            ruta,
            contexto.asignaciones,
            ids_recblue_por_operacion=ids_recblue,
        )
        logger.info("Entregable: %s", ruta)
        return contexto

    def _resolver_ruta_asignacion(self, contexto: ProcesoContext) -> Path:
        if not contexto.creditos or self._directorio_destino is None:
            return contexto.archivo_asignacion
        fecha_archivo = contexto.creditos[0].fecha_corte
        feriados = (
            self._feriados.fechas_vigentes()
            if self._feriados is not None
            else set()
        )
        return ruta_asignacion_desde_fecha_archivo(
            self._directorio_destino,
            fecha_archivo,
            set(feriados),
        )
