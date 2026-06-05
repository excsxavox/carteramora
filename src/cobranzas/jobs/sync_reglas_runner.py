import logging
import sys

from cobranzas.domain.services.sembrar_reglas_mora_service import SembrarReglasMoraService
from cobranzas.infrastructure.config.settings import Settings
from cobranzas.infrastructure.persistence.database import (
    create_engine_from_settings,
    init_database,
)
from cobranzas.infrastructure.persistence.repositories.reglas_repository import (
    SqlAlchemyReglasRepository,
)
from cobranzas.infrastructure.persistence.session import get_session_factory
from cobranzas.jobs.container import _lista_csv


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> int:
    """Sembrar tabla reglas desde .env si está vacía."""
    settings = Settings()
    _configure_logging(settings.log_level)
    logger = logging.getLogger("cobranzas.job.sync_reglas")

    engine = create_engine_from_settings(settings)
    init_database(engine)
    repo = SqlAlchemyReglasRepository(get_session_factory(engine))
    antes = repo.contar_reglas()
    insertadas = SembrarReglasMoraService(repo).sembrar_si_vacio(
        estados_excluidos=_lista_csv(settings.estados_excluidos),
        tipos_oper_excluidos=_lista_csv(settings.tipos_oper_excluidos),
        dias_min=settings.mora_temprana_dias_min,
        dias_max=settings.mora_temprana_dias_max,
    )
    despues = repo.contar_reglas()
    if insertadas:
        logger.info("Reglas insertadas: %s (total=%s)", insertadas, despues)
    else:
        logger.info(
            "Sin cambios: la tabla reglas ya tenía %s fila(s)", antes
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
