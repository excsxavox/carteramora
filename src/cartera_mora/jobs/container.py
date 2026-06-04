"""Composition root: ensambla dependencias (inyección manual)."""

from typing import Optional

from cartera_mora.application.use_cases.procesar_cartera_mora import (
    ProcesarCarteraMoraUseCase,
)
from cartera_mora.domain.services.cartera_mora_service import CarteraMoraService
from cartera_mora.domain.services.cartera_merge_service import CarteraMergeService
from cartera_mora.domain.services.manifiesto_lis_service import ManifiestoLisService
from cartera_mora.infrastructure.adapters.json_reporte_repository import (
    JsonReporteRepository,
)
from cartera_mora.infrastructure.adapters.lis_manifiesto_repository import (
    LisManifiestoRepository,
)
from cartera_mora.infrastructure.adapters.tsv_credito_repository import (
    TsvCreditoRepository,
)
from cartera_mora.infrastructure.adapters.tsv_cartera_repository import (
    TsvCarteraRepository,
)
from cartera_mora.infrastructure.config.settings import Settings


def build_procesar_cartera_mora_use_case(
    settings: Optional[Settings] = None,
) -> ProcesarCarteraMoraUseCase:
    cfg = settings or Settings()
    return ProcesarCarteraMoraUseCase.crear(
        morosidad_repository=TsvCreditoRepository(cfg.archivo_morosidad),
        cartera_repository=TsvCarteraRepository(cfg.archivo_cartera),
        reporte_repository=JsonReporteRepository(cfg.archivo_salida),
        manifiesto_repository=LisManifiestoRepository(cfg.archivo_lis),
        cartera_mora_service=CarteraMoraService(),
        cartera_merge_service=CarteraMergeService(),
        manifiesto_lis_service=ManifiestoLisService(),
        dias_mora_minimo=cfg.dias_mora_minimo,
        archivo_morosidad=cfg.archivo_morosidad,
        archivo_cartera=cfg.archivo_cartera,
        archivo_reporte=cfg.archivo_salida,
        archivo_lis=cfg.archivo_lis,
    )
