import logging
from datetime import date
from typing import Optional

from cobranzas.application.chain.handler import Handler
from cobranzas.application.chain.proceso_context import ProcesoContext
from cobranzas.domain.ports.feriados_calendario_port import FeriadosCalendarioPort
from cobranzas.domain.services.exportar_acumulado_mensual_service import (
    ExportarAcumuladoMensualService,
)

logger = logging.getLogger(__name__)


class ExportAcumuladoHandler(Handler):
    """Entregable HU-GRC-01: Excel acumulado mensual (deuda + asesores_deuda)."""

    def __init__(
        self,
        export_service: ExportarAcumuladoMensualService,
        feriados_repository: Optional[FeriadosCalendarioPort] = None,
    ) -> None:
        super().__init__()
        self._export = export_service
        self._feriados = feriados_repository

    def _procesar(self, contexto: ProcesoContext) -> ProcesoContext:
        if not contexto.persistir_en_bd or contexto.registros_persistidos_bd <= 0:
            return contexto
        if not contexto.usar_mora_temprana:
            return contexto

        fecha_archivo = self._resolver_fecha_archivo(contexto)
        if fecha_archivo is None:
            return contexto

        feriados = (
            self._feriados.fechas_vigentes()
            if self._feriados is not None
            else frozenset()
        )
        archivo = self._export.exportar(
            fecha_archivo, set(feriados), es_fin_de_mes=contexto.es_fin_de_mes
        )
        contexto.archivo_acumulado_mensual = archivo
        logger.info("Entregable acumulado: %s", archivo)
        return contexto

    @staticmethod
    def _resolver_fecha_archivo(contexto: ProcesoContext) -> Optional[date]:
        if contexto.creditos_mora:
            return contexto.creditos_mora[0].fecha_corte
        if contexto.creditos:
            return contexto.creditos[0].fecha_corte
        return None
