import logging
import sys

from cobranzas.infrastructure.config.settings import Settings
from cobranzas.jobs.staging_container import build_cargar_staging_use_case


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> int:
    """Job 2: carga detalle_morosidad.lis y reporte_mora.lis a tablas temporales."""
    settings = Settings()
    _configure_logging(settings.log_level)
    logger = logging.getLogger("cobranzas.job.staging")

    logger.info("Iniciando job de carga a tablas temporales")
    logger.info("Archivo morosidad limpio: %s", settings.archivo_salida_morosidad)
    logger.info("Archivo mora limpio: %s", settings.archivo_salida_mora)
    logger.info("Base de datos: %s", settings.database_url)
    logger.info(
        "Logs contenido .lis: logger=cobranzas.archivo.lis | muestras=%s (LOG_MUESTRA_MAPEO)",
        settings.log_muestra_mapeo,
    )

    try:
        use_case = build_cargar_staging_use_case(settings)
        result = use_case.ejecutar()
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        logger.error(
            "Ejecute primero el job de limpieza (python main.py) para generar los .lis"
        )
        return 1
    except Exception:
        logger.exception("Error en carga staging")
        return 1

    logger.info(
        "Carga finalizada | lote=%s | morosidad=%s filas (%s cols) | mora=%s filas (%s cols)",
        result.id_lote,
        result.filas_morosidad,
        result.columnas_morosidad,
        result.filas_mora,
        result.columnas_mora,
    )
    logger.info(
        "Tablas: tmp_lote_carga, tmp_columna_archivo, tmp_stg_morosidad, tmp_stg_mora"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
