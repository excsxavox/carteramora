"""Composition root: ensambla dependencias (inyección manual)."""

from typing import Optional

from cobranzas.application.use_cases.procesar_cobranzas import (
    ProcesarCobranzasUseCase,
)
from cobranzas.domain.services.cobranzas_service import CobranzasService
from cobranzas.domain.services.cartera_merge_service import CarteraMergeService
from cobranzas.domain.services.manifiesto_lis_service import ManifiestoLisService
from cobranzas.infrastructure.adapters.json_reporte_repository import (
    JsonReporteRepository,
)
from cobranzas.infrastructure.adapters.lis_manifiesto_repository import (
    LisManifiestoRepository,
)
from cobranzas.infrastructure.adapters.tsv_credito_repository import (
    TsvCreditoRepository,
)
from cobranzas.infrastructure.adapters.tsv_cartera_repository import (
    TsvCarteraRepository,
)
from cobranzas.infrastructure.config.settings import Settings


def build_procesar_cobranzas_use_case(
    settings: Optional[Settings] = None,
) -> ProcesarCobranzasUseCase:
    cfg = settings or Settings()
    return ProcesarCobranzasUseCase.crear(
        morosidad_repository=TsvCreditoRepository(cfg.archivo_morosidad),
        cartera_repository=TsvCarteraRepository(cfg.archivo_cartera),
        reporte_repository=JsonReporteRepository(cfg.archivo_salida),
        manifiesto_repository=LisManifiestoRepository(cfg.archivo_lis),
        cobranzas_service=CobranzasService(),
        cartera_merge_service=CarteraMergeService(),
        manifiesto_lis_service=ManifiestoLisService(),
        dias_mora_minimo=cfg.dias_mora_minimo,
        archivo_morosidad=cfg.archivo_morosidad,
        archivo_cartera=cfg.archivo_cartera,
        archivo_reporte=cfg.archivo_salida,
        archivo_lis=cfg.archivo_lis,
    )
