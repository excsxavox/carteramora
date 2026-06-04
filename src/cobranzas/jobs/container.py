"""Composition root: ensambla dependencias (inyección manual)."""

from typing import Optional

from cobranzas.application.use_cases.procesar_cobranzas import (
    ProcesarCobranzasUseCase,
)
from cobranzas.domain.services.cobranzas_service import CobranzasService
from cobranzas.domain.services.cartera_merge_service import CarteraMergeService
from cobranzas.domain.services.persistir_cartera_mora_service import (
    PersistirCarteraMoraService,
)
from cobranzas.infrastructure.adapters.tsv_credito_repository import (
    TsvCreditoRepository,
)
from cobranzas.infrastructure.adapters.tsv_cartera_repository import (
    TsvCarteraRepository,
)
from cobranzas.infrastructure.config.settings import Settings
from cobranzas.infrastructure.persistence.database import (
    create_engine_from_settings,
    init_database,
)
from cobranzas.infrastructure.persistence.repositories import SqlAlchemyCobranzaRepository
from cobranzas.infrastructure.persistence.session import get_session_factory


def build_procesar_cobranzas_use_case(
    settings: Optional[Settings] = None,
) -> ProcesarCobranzasUseCase:
    cfg = settings or Settings()
    persistir_service: Optional[PersistirCarteraMoraService] = None

    if cfg.persistir_en_bd:
        engine = create_engine_from_settings(cfg)
        init_database(engine)
        session_factory = get_session_factory(engine)
        persistir_service = PersistirCarteraMoraService(
            SqlAlchemyCobranzaRepository(session_factory, cfg.dias_mora_minimo),
            dias_mora_minimo=cfg.dias_mora_minimo,
        )

    return ProcesarCobranzasUseCase.crear(
        morosidad_repository=TsvCreditoRepository(cfg.archivo_morosidad),
        cartera_repository=TsvCarteraRepository(cfg.archivo_cartera),
        cobranzas_service=CobranzasService(),
        cartera_merge_service=CarteraMergeService(),
        dias_mora_minimo=cfg.dias_mora_minimo,
        archivo_morosidad=cfg.archivo_morosidad,
        archivo_cartera=cfg.archivo_cartera,
        archivo_detalle_morosidad=cfg.archivo_salida_morosidad,
        archivo_detalle_mora=cfg.archivo_salida_mora,
        persistir_service=persistir_service,
        persistir_en_bd=cfg.persistir_en_bd,
        database_url=cfg.database_url,
    )
