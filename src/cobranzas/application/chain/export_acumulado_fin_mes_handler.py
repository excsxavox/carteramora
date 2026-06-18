import logging
from datetime import date
from typing import Optional, Set

from cobranzas.application.chain.handler import Handler
from cobranzas.application.chain.proceso_context import ProcesoContext
from cobranzas.domain.services.exportar_acumulado_fin_mes_service import (
    ExportarAcumuladoFinMesService,
)

logger = logging.getLogger(__name__)


class ExportAcumuladoFinMesHandler(Handler):
    """Entregable fin de mes: unificación CAMOROSICO + CADETACACO, sin filtro de mora."""

    def __init__(
        self,
        export_service: ExportarAcumuladoFinMesService,
        feriados: Optional[Set[date]] = None,
    ) -> None:
        super().__init__()
        self._export = export_service
        self._feriados = feriados or set()

    def _procesar(self, contexto: ProcesoContext) -> ProcesoContext:
        fecha_archivo = self._resolver_fecha_archivo(contexto)
        if fecha_archivo is None:
            return contexto

        archivo = self._export.exportar(
            contexto.creditos,
            fecha_archivo,
            self._feriados,
            archivo_origen=str(contexto.archivo_morosidad),
        )
        contexto.archivo_acumulado_fin_mes = archivo
        logger.info("Entregable acumulado fin mes: %s", archivo)
        return contexto

    @staticmethod
    def _resolver_fecha_archivo(contexto: ProcesoContext) -> Optional[date]:
        if contexto.creditos:
            return contexto.creditos[0].fecha_corte
        if contexto.creditos_mora:
            return contexto.creditos_mora[0].fecha_corte
        return None
