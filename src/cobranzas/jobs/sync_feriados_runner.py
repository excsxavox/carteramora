import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from cobranzas.infrastructure.config.database_url import resolver_database_url
from cobranzas.infrastructure.config.settings import Settings
from cobranzas.jobs.sync_feriados_container import build_sincronizar_feriados_use_case


def _configure_logging(settings: Settings) -> None:
    nivel = getattr(logging, settings.log_level.upper(), logging.INFO)
    formato = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    handlers: list[logging.Handler] = [logging.StreamHandler()]

    log_dir = settings.log_dir
    log_dir.mkdir(parents=True, exist_ok=True)
    archivo_log = log_dir / f"actualizar_feriados_{datetime.now():%Y%m%d_%H%M%S}.log"
    handlers.append(logging.FileHandler(archivo_log, encoding="utf-8"))

    logging.basicConfig(level=nivel, format=formato, handlers=handlers, force=True)


def ejecutar_sync_feriados(settings: Optional[Settings] = None) -> int:
    """Job 0b: Excel de feriados → catálogo (claves/catalogo)."""
    cfg = settings or Settings()
    logger = logging.getLogger("cobranzas.job.sync_feriados")

    logger.info(
        "Job 0b: feriados %s/%s → BD %s",
        cfg.directorio_excel_feriados,
        cfg.patron_excel_feriados,
        resolver_database_url(cfg),
    )

    try:
        resultado = build_sincronizar_feriados_use_case(cfg).ejecutar()
    except Exception:
        logger.exception("Error en sincronización de feriados")
        return 1

    if resultado.omitidos_sin_excel:
        logger.warning(
            "Sin Excel de feriados en '%s' (%s); se usa catálogo existente en BD.",
            cfg.directorio_excel_feriados,
            cfg.patron_excel_feriados,
        )
        return 0

    if resultado.errores:
        for error in resultado.errores:
            logger.error("%s", error)
        return 1

    logger.info(
        "Job 0b finalizado | archivo=%s registros=%s insertados=%s activados=%s desactivados=%s",
        resultado.archivo_excel,
        resultado.registros_excel,
        resultado.dias_insertados,
        resultado.dias_activados,
        resultado.dias_desactivados,
    )
    return 0


def main() -> int:
    settings = Settings()
    _configure_logging(settings)
    return ejecutar_sync_feriados(settings)


if __name__ == "__main__":
    sys.exit(main())
