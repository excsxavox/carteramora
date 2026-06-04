from typing import Optional

from cobranzas.application.use_cases.cargar_staging import CargarStagingUseCase
from cobranzas.domain.services.cargar_staging_service import CargarStagingService
from cobranzas.infrastructure.config.settings import Settings
from cobranzas.infrastructure.persistence.database import (
    create_engine_from_settings,
    init_database,
)
from cobranzas.infrastructure.logging.archivo_lis_logger import ArchivoLisLogger
from cobranzas.infrastructure.persistence.repositories.staging_repository import (
    SqlAlchemyStagingRepository,
)
from cobranzas.infrastructure.persistence.session import get_session_factory

# Registra modelos staging en metadata antes de create_all
from cobranzas.infrastructure.persistence.models import staging as _staging_models  # noqa: F401


def build_cargar_staging_use_case(
    settings: Optional[Settings] = None,
) -> CargarStagingUseCase:
    cfg = settings or Settings()
    engine = create_engine_from_settings(cfg)
    init_database(engine)
    repository = SqlAlchemyStagingRepository(
        get_session_factory(engine),
        archivo_logger=ArchivoLisLogger(cfg.log_muestra_mapeo),
    )
    service = CargarStagingService(repository)
    return CargarStagingUseCase(service, cfg)
