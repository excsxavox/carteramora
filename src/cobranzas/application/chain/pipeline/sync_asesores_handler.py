import logging

from cobranzas.application.chain.pipeline.pipeline_context import PipelineContext
from cobranzas.application.chain.pipeline.pipeline_handler import PipelineHandler
from cobranzas.jobs.sync_asesores_container import build_sincronizar_asesores_use_case

logger = logging.getLogger("cobranzas.pipeline.sync_asesores")


class SyncAsesoresPipelineHandler(PipelineHandler):
    """Job 0: Excel → tabla asesores."""

    def _procesar(self, contexto: PipelineContext) -> PipelineContext:
        logger.info("--- Cadena: Job 0 asesores ---")
        cfg = contexto.settings
        try:
            resultado = build_sincronizar_asesores_use_case(cfg).ejecutar()
        except FileNotFoundError as exc:
            logger.error("%s", exc)
            contexto.codigo_salida = 1
            contexto.detener = True
            contexto.mensajes.append(str(exc))
            return contexto
        except Exception as exc:
            logger.exception("Error en sincronización de asesores")
            contexto.codigo_salida = 1
            contexto.detener = True
            contexto.mensajes.append(str(exc))
            return contexto

        if resultado.errores:
            contexto.codigo_salida = 1
            contexto.detener = True
            contexto.mensajes.extend(resultado.errores)
            return contexto

        logger.info(
            "Job 0 OK | creados=%s actualizados=%s sin_cambios=%s",
            resultado.creados,
            resultado.actualizados,
            resultado.sin_cambios,
        )
        return contexto
