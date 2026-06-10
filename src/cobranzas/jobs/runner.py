import logging
import sys

from cobranzas.jobs.container import build_procesar_cobranzas_use_case
from cobranzas.infrastructure.config.settings import Settings


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> int:
    """Punto de entrada del job."""
    settings = Settings()
    _configure_logging(settings.log_level)
    logger = logging.getLogger("cobranzas.job")

    logger.info("Iniciando job de cartera en mora")
    logger.info("Lee morosidad: %s", settings.archivo_morosidad)
    logger.info("Lee cartera: %s", settings.archivo_cartera)
    logger.info("Genera salida 1: %s", settings.archivo_salida_morosidad)
    logger.info("Genera salida 2: %s", settings.archivo_salida_mora)
    try:
        use_case = build_procesar_cobranzas_use_case(settings)
        result = use_case.ejecutar()
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        return 1
    except Exception:
        logger.exception("Error inesperado en el job")
        return 1

    logger.info(
        "Job finalizado | procesados=%s en_mora=%s saldo_mora=%.2f",
        result.total_creditos_procesados,
        result.total_en_mora,
        result.total_saldo_mora,
    )
    logger.info("Archivos generados: %s | %s", result.archivo_detalle_morosidad, result.archivo_detalle_mora)
    if result.registros_persistidos_bd:
        logger.info("Registros guardados en BD: %s", result.registros_persistidos_bd)
    if result.asignaciones_generadas:
        logger.info(
            "ASIGNACION.csv | filas=%s | %s",
            result.asignaciones_generadas,
            result.archivo_asignacion,
        )
    if result.archivo_acumulado_mensual:
        logger.info("Acumulado mensual: %s", result.archivo_acumulado_mensual)
    return 0


if __name__ == "__main__":
    sys.exit(main())
