"""Pipeline único: python main.py → todo el flujo diario."""

import logging
import sys

from cobranzas.application.chain.pipeline import PipelineContext, build_pipeline_chain
from cobranzas.infrastructure.config.database_url import resolver_database_url
from cobranzas.infrastructure.config.settings import Settings
from cobranzas.infrastructure.persistence.database import (
    create_engine_from_settings,
    init_database,
    verificar_conexion,
)
from cobranzas.jobs.runner import _configure_logging

logger = logging.getLogger("cobranzas.pipeline")


def _preparar_base_datos(settings: Settings) -> None:
    """Verifica conexión y crea tablas si no existen (sin migrar esquema)."""
    if not settings.persistir_en_bd and not settings.usar_mora_temprana:
        logger.info("Sin persistencia ni mora temprana: se omite init de BD")
        return

    engine = create_engine_from_settings(settings)
    init_database(engine)
    verificar_conexion(engine)
    logger.info("Base de datos lista: %s", resolver_database_url(settings))


def _log_plan(settings: Settings) -> None:
    logger.info("=== Plan pipeline (python main.py) ===")
    logger.info("1. Job 0  — Excel asesores → %s", settings.archivo_excel_asesores)
    logger.info(
        "2. Job 0b — Excel feriados → %s / %s (clave %s)",
        settings.directorio_excel_feriados,
        settings.patron_excel_feriados,
        settings.clave_feriados,
    )
    logger.info("3. Job 1  — Limpieza CAMOROSICO + CADETACACO")
    if settings.usar_mora_temprana:
        logger.info("         — Mora temprana, asignación, %s", settings.archivo_salida_asignacion)
    if settings.archivo_recblue:
        logger.info("         — Recblue: %s", settings.archivo_recblue)
    if settings.persistir_en_bd:
        logger.info("         — Persistencia BD (deudores, deuda, asesores_deuda)")
    if settings.incluir_staging_en_pipeline:
        logger.info("4. Job 2  — Staging tmp_* desde .lis limpios")


def main() -> int:
    settings = Settings()
    _configure_logging(settings.log_level)

    try:
        _log_plan(settings)
        _preparar_base_datos(settings)

        contexto = PipelineContext(settings=settings)
        contexto = build_pipeline_chain().manejar(contexto)

        if contexto.codigo_salida == 0:
            logger.info("=== Pipeline finalizado correctamente ===")
        else:
            logger.error("=== Pipeline detenido (código %s) ===", contexto.codigo_salida)
            for msg in contexto.mensajes:
                logger.error("  %s", msg)

        return contexto.codigo_salida
    except Exception:
        logger.exception("Error fatal en pipeline")
        return 1


if __name__ == "__main__":
    sys.exit(main())
