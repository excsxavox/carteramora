import logging
import sys

from cobranzas.infrastructure.config.settings import Settings
from cobranzas.jobs.sync_asesores_container import build_sincronizar_asesores_use_case


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> int:
    """Job 0: sincroniza tabla asesores desde Excel (antes de limpieza)."""
    settings = Settings()
    _configure_logging(settings.log_level)
    logger = logging.getLogger("cobranzas.job.sync_asesores")

    logger.info("=== Job 0: Sincronización asesores desde Excel ===")
    logger.info("Archivo Excel: %s", settings.archivo_excel_asesores)
    logger.info("Base de datos: %s", settings.database_url)

    try:
        resultado = build_sincronizar_asesores_use_case(settings).ejecutar()
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        logger.error(
            "Cree la plantilla: python scripts/crear_plantilla_asesores.py"
        )
        return 1
    except Exception:
        logger.exception("Error en sincronización de asesores")
        return 1

    if resultado.errores:
        return 1

    logger.info(
        "Job 0 finalizado | excel=%s únicos=%s creados=%s actualizados=%s sin_cambios=%s",
        resultado.filas_excel or resultado.total_leidos,
        resultado.total_leidos,
        resultado.creados,
        resultado.actualizados,
        resultado.sin_cambios,
    )
    logger.info("Siguiente paso: python main.py (limpieza cartera)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
