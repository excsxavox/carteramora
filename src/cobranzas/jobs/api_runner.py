import logging
import sys

from cobranzas.infrastructure.config.settings import Settings
from cobranzas.jobs.runner import _configure_logging

logger = logging.getLogger("cobranzas.api")


def main() -> int:
    """Inicia servidor HTTP (FastAPI + uvicorn)."""
    try:
        import uvicorn
    except ImportError as exc:
        logger.error(
            "Instale dependencias API: pip install -e \".[api]\""
        )
        raise SystemExit(1) from exc

    settings = Settings(DEFERIR_RESOLUCION_RUTAS=True)
    _configure_logging(settings.log_level)
    base = f"http://{settings.api_host}:{settings.api_port}"
    logger.info("API en %s", base)
    logger.info("Swagger UI: %s/docs", base)
    logger.info("ReDoc:       %s/redoc", base)
    logger.info('POST /pipeline  body: {"fecha": "05052026"}')

    uvicorn.run(
        "cobranzas.api.app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
