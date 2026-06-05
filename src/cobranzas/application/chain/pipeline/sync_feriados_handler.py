import logging

from cobranzas.application.chain.pipeline.pipeline_context import PipelineContext
from cobranzas.application.chain.pipeline.pipeline_handler import PipelineHandler
from cobranzas.jobs.sync_feriados_container import build_sincronizar_feriados_use_case

logger = logging.getLogger("cobranzas.pipeline.sync_feriados")


class SyncFeriadosPipelineHandler(PipelineHandler):
    """Job 0b: Excel → catálogo feriados (después de asesores)."""

    def _procesar(self, contexto: PipelineContext) -> PipelineContext:
        cfg = contexto.settings
        try:
            resultado = build_sincronizar_feriados_use_case(cfg).ejecutar()
        except Exception as exc:
            logger.exception("Error en sincronización de feriados")
            contexto.codigo_salida = 1
            contexto.detener = True
            contexto.mensajes.append(str(exc))
            return contexto

        if resultado.omitidos_sin_excel:
            logger.debug(
                "Sin Excel de feriados en '%s' (%s); se usa catálogo existente en BD.",
                cfg.directorio_excel_feriados,
                cfg.patron_excel_feriados,
            )
            return contexto

        logger.info("--- Cadena: Job 0b feriados ---")
        if resultado.errores:
            contexto.codigo_salida = 1
            contexto.detener = True
            contexto.mensajes.extend(resultado.errores)
            return contexto

        logger.info(
            "Job 0b OK | insertados=%s activados=%s desactivados=%s",
            resultado.dias_insertados,
            resultado.dias_activados,
            resultado.dias_desactivados,
        )
        return contexto
