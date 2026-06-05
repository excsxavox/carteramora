import logging
import sys
from typing import Optional

from cobranzas.infrastructure.config.settings import Settings
from cobranzas.jobs.staging_container import build_cargar_staging_use_case


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def ejecutar_staging(settings: Optional[Settings] = None) -> int:
    """Job 2: carga .lis limpios a tablas tmp_*."""
    cfg = settings or Settings()
    logger = logging.getLogger("cobranzas.job.staging")
    logger.info("Archivo morosidad limpio: %s", cfg.archivo_salida_morosidad)
    logger.info("Archivo mora limpio: %s", cfg.archivo_salida_mora)

    try:
        result = build_cargar_staging_use_case(cfg).ejecutar()
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        return 1
    except Exception:
        logger.exception("Error en carga staging")
        return 1

    logger.info(
        "Staging OK | lote=%s | morosidad=%s | mora=%s",
        result.id_lote,
        result.filas_morosidad,
        result.filas_mora,
    )
    return 0


def main() -> int:
    """Job 2: carga detalle_morosidad.lis y reporte_mora.lis a tablas temporales."""
    settings = Settings()
    _configure_logging(settings.log_level)
    logger = logging.getLogger("cobranzas.job.staging")

    logger.info("Iniciando job de carga a tablas temporales")
    logger.info("Archivo morosidad limpio: %s", settings.archivo_salida_morosidad)
    logger.info("Archivo mora limpio: %s", settings.archivo_salida_mora)
    logger.info("Base de datos: %s", settings.database_url)

    return ejecutar_staging(settings)


if __name__ == "__main__":
    sys.exit(main())
