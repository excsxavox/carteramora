from typing import Optional

from cobranzas.application.use_cases.sincronizar_feriados import SincronizarFeriadosUseCase
from cobranzas.domain.services.sincronizar_feriados_service import SincronizarFeriadosService
from cobranzas.infrastructure.adapters.excel_feriado_reader import ExcelFeriadoReader
from cobranzas.infrastructure.config.settings import Settings
from cobranzas.infrastructure.persistence.database import (
    create_engine_from_settings,
    init_database,
)
from cobranzas.infrastructure.persistence.repositories.feriado_catalogo_repository import (
    SqlAlchemyFeriadoCatalogoRepository,
)
from cobranzas.infrastructure.persistence.session import get_session_factory


def build_sincronizar_feriados_use_case(
    settings: Optional[Settings] = None,
) -> SincronizarFeriadosUseCase:
    cfg = settings or Settings()
    engine = create_engine_from_settings(cfg)
    init_database(engine)
    service = SincronizarFeriadosService(
        ExcelFeriadoReader(),
        SqlAlchemyFeriadoCatalogoRepository(get_session_factory(engine)),
        directorio_excel=cfg.directorio_excel_feriados,
        patron_excel=cfg.patron_excel_feriados,
        clave_feriados=cfg.clave_feriados,
    )
    return SincronizarFeriadosUseCase(service)
