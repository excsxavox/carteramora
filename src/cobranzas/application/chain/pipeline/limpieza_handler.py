import logging

from cobranzas.application.chain.pipeline.pipeline_context import PipelineContext
from cobranzas.application.chain.pipeline.pipeline_handler import PipelineHandler
from cobranzas.jobs.container import build_procesar_cobranzas_use_case

logger = logging.getLogger("cobranzas.pipeline.limpieza")


class LimpiezaPipelineHandler(PipelineHandler):
    """Job 1: core .lis → destino + persistencia BD."""

    def _procesar(self, contexto: PipelineContext) -> PipelineContext:
        logger.info("--- Cadena: Job 1 limpieza cartera ---")
        cfg = contexto.settings
        try:
            result = build_procesar_cobranzas_use_case(cfg).ejecutar()
        except FileNotFoundError as exc:
            logger.error("%s", exc)
            contexto.codigo_salida = 1
            contexto.detener = True
            contexto.mensajes.append(str(exc))
            return contexto
        except Exception as exc:
            logger.exception("Error en limpieza de cartera")
            contexto.codigo_salida = 1
            contexto.detener = True
            contexto.mensajes.append(str(exc))
            return contexto

        logger.info(
            "Job 1 OK | procesados=%s en_mora=%s saldo_mora=%.2f",
            result.total_creditos_procesados,
            result.total_en_mora,
            result.total_saldo_mora,
        )
        if result.registros_persistidos_bd:
            logger.info("Registros en BD: %s", result.registros_persistidos_bd)
        logger.info(
            "ASIGNACION.csv | filas=%s | %s",
            result.asignaciones_generadas,
            result.archivo_asignacion,
        )
        if result.archivo_acumulado_mensual:
            logger.info("Acumulado mensual: %s", result.archivo_acumulado_mensual)
        logger.info("Salidas: %s | %s", result.archivo_detalle_morosidad, result.archivo_detalle_mora)
        contexto.resultado_limpieza = result
        return contexto
