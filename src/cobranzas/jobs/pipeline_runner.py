import logging
import sys

from cobranzas.infrastructure.config.settings import Settings
from cobranzas.jobs.runner import _configure_logging, main as job_limpieza
from cobranzas.jobs.sync_asesores_runner import main as job_sync_asesores


def main() -> int:
    """Ejecuta Job 0 (Excel → asesores) y Job 1 (limpieza cartera) en secuencia."""
    settings = Settings()
    _configure_logging(settings.log_level)
    logger = logging.getLogger("cobranzas.pipeline")

    logger.info("=== Pipeline: Job 0 + Job 1 ===")

    codigo = job_sync_asesores()
    if codigo != 0:
        logger.error("Pipeline detenido: falló sincronización de asesores")
        return codigo

    logger.info("--- Job 0 OK. Iniciando Job 1 (limpieza) ---")
    codigo = job_limpieza()
    if codigo != 0:
        logger.error("Pipeline detenido: falló limpieza de cartera")
        return codigo

    logger.info("=== Pipeline finalizado correctamente ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
