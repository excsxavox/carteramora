from typing import Optional

from cobranzas.application.chain.handler import Handler
from cobranzas.application.chain.lectura_cartera_handler import LecturaCarteraHandler
from cobranzas.application.chain.lectura_morosidad_handler import LecturaMorosidadHandler
from cobranzas.application.chain.persistencia_bd_handler import PersistenciaBDHandler
from cobranzas.application.chain.reporte_handler import ProcesamientoMoraHandler
from cobranzas.domain.ports.cartera_repository import CarteraRepositoryPort
from cobranzas.domain.ports.credito_repository import CreditoRepositoryPort
from cobranzas.domain.services.cobranzas_service import CobranzasService
from cobranzas.domain.services.cartera_merge_service import CarteraMergeService
from cobranzas.domain.services.persistir_cartera_mora_service import (
    PersistirCarteraMoraService,
)
from cobranzas.domain.services.tab_detalle_export_service import (
    TabDetalleExportService,
)


def build_proceso_chain(
    morosidad_repository: CreditoRepositoryPort,
    cartera_repository: CarteraRepositoryPort,
    cobranzas_service: CobranzasService,
    cartera_merge_service: CarteraMergeService,
    tab_detalle_export_service: Optional[TabDetalleExportService] = None,
    persistir_service: Optional[PersistirCarteraMoraService] = None,
) -> Handler:
    """Cadena: morosidad -> cartera -> exportación -> persistencia BD (opcional)."""
    morosidad = LecturaMorosidadHandler(morosidad_repository)
    cartera = LecturaCarteraHandler(cartera_repository, cartera_merge_service)
    procesamiento = ProcesamientoMoraHandler(
        cobranzas_service,
        tab_detalle_export_service or TabDetalleExportService(),
    )
    morosidad.enlazar(cartera).enlazar(procesamiento)

    if persistir_service is not None:
        procesamiento.enlazar(PersistenciaBDHandler(persistir_service))

    return morosidad
