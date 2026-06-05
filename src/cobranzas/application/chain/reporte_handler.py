import logging

from cobranzas.application.chain.handler import Handler
from cobranzas.application.chain.proceso_context import ProcesoContext
from cobranzas.domain.services.cobranzas_service import CobranzasService
from cobranzas.domain.schemas.tab_schema import COL_CLASIFICACION_MORA, unificar_columnas_tab
from cobranzas.domain.services.tab_detalle_export_service import (
    TabDetalleExportService,
)
from cobranzas.infrastructure.adapters.tab_lis_staging_reader import parsear_archivo_tab
from cobranzas.infrastructure.config.settings import Settings
from cobranzas.infrastructure.logging.archivo_lis_logger import ArchivoLisLogger

logger = logging.getLogger(__name__)


class ProcesamientoMoraHandler(Handler):
    """Paso 3: filtra mora y genera los 2 archivos TAB de salida."""

    def __init__(
        self,
        cobranzas_service: CobranzasService,
        tab_detalle_export_service: TabDetalleExportService,
    ) -> None:
        super().__init__()
        self._service = cobranzas_service
        self._tab_export = tab_detalle_export_service

    def _procesar(self, contexto: ProcesoContext) -> ProcesoContext:
        if contexto.usar_mora_temprana:
            creditos_mora = list(contexto.creditos)
        else:
            creditos_mora = self._service.filtrar_en_mora(
                contexto.creditos, contexto.dias_mora_minimo
            )
        contexto.creditos_mora = creditos_mora
        contexto.reporte = self._service.construir_reporte(
            creditos_mora, contexto.dias_mora_minimo
        )
        contexto.columnas_mora = unificar_columnas_tab(
            contexto.columnas_morosidad,
            contexto.columnas_cartera,
            extra=(COL_CLASIFICACION_MORA,),
        )

        self._tab_export.exportar_morosidad(
            contexto.archivo_detalle_morosidad,
            contexto.columnas_morosidad,
            contexto.creditos_morosidad,
        )
        self._tab_export.exportar_mora(
            contexto.archivo_detalle_mora,
            contexto.columnas_mora,
            creditos_mora,
            contexto.dias_mora_minimo,
        )

        logger.info(
            "Procesamiento | en_mora=%s saldo=%.2f | %s | %s",
            contexto.reporte["total_creditos"],
            contexto.reporte["total_saldo_mora"],
            contexto.archivo_detalle_morosidad,
            contexto.archivo_detalle_mora,
        )
        self._log_contenido_archivos_generados(
            contexto.archivo_detalle_morosidad,
            contexto.archivo_detalle_mora,
        )
        return contexto

    def _log_contenido_archivos_generados(self, morosidad, mora) -> None:
        cfg = Settings()
        if cfg.log_muestra_mapeo <= 0:
            return
        if not morosidad.is_file() or not mora.is_file():
            return
        archivo_log = ArchivoLisLogger(cfg.log_muestra_mapeo)
        archivo_log.log_inicio(morosidad, mora)
        for ruta in (morosidad, mora):
            try:
                archivo_log.log_archivo(ruta, parsear_archivo_tab(ruta))
            except ValueError:
                logger.warning("Archivo sin filas para log: %s", ruta)
