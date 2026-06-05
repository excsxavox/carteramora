import logging

from cobranzas.application.chain.pipeline.pipeline_context import PipelineContext
from cobranzas.application.chain.pipeline.pipeline_handler import PipelineHandler

logger = logging.getLogger("cobranzas.pipeline.staging")


class StagingPipelineHandler(PipelineHandler):
    """Job 2: carga .lis limpios a tablas tmp_*."""

    def _procesar(self, contexto: PipelineContext) -> PipelineContext:
        if not contexto.settings.incluir_staging_en_pipeline:
            return contexto

        logger.info("--- Cadena: Job 2 staging ---")
        from cobranzas.jobs.cargar_staging_runner import ejecutar_staging

        codigo = ejecutar_staging(contexto.settings)
        if codigo != 0:
            contexto.codigo_salida = codigo
            contexto.detener = True
            contexto.mensajes.append("Falló carga staging")
        return contexto
