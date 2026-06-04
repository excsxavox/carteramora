from typing import Optional

from cobranzas.application.use_cases.sincronizar_asesores import SincronizarAsesoresUseCase
from cobranzas.domain.services.sincronizar_asesores_service import (
    SincronizarAsesoresService,
)
from cobranzas.infrastructure.adapters.excel_asesor_reader import ExcelAsesorReader
from cobranzas.infrastructure.config.settings import Settings
from cobranzas.infrastructure.persistence.database import (
    create_engine_from_settings,
    init_database,
)
from cobranzas.infrastructure.persistence.repositories.asesor_sync_repository import (
    SqlAlchemyAsesorSyncRepository,
)
from cobranzas.infrastructure.persistence.session import get_session_factory


def build_sincronizar_asesores_use_case(
    settings: Optional[Settings] = None,
) -> SincronizarAsesoresUseCase:
    cfg = settings or Settings()
    engine = create_engine_from_settings(cfg)
    init_database(engine)
    service = SincronizarAsesoresService(
        ExcelAsesorReader(),
        SqlAlchemyAsesorSyncRepository(get_session_factory(engine)),
        rechazar_duplicados_excel=cfg.sync_asesores_rechazar_duplicados,
    )
    return SincronizarAsesoresUseCase(service, cfg)
