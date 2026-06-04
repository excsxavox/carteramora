from cobranzas.application.chain.handler import Handler
from cobranzas.application.chain.lectura_cartera_handler import LecturaCarteraHandler
from cobranzas.application.chain.lectura_morosidad_handler import LecturaMorosidadHandler
from cobranzas.application.chain.reporte_handler import ProcesamientoMoraHandler
from cobranzas.domain.ports.cartera_repository import CarteraRepositoryPort
from cobranzas.domain.ports.credito_repository import CreditoRepositoryPort
from cobranzas.domain.ports.manifiesto_repository import ManifiestoRepositoryPort
from cobranzas.domain.ports.reporte_repository import ReporteRepositoryPort
from cobranzas.domain.services.cobranzas_service import CobranzasService
from cobranzas.domain.services.cartera_merge_service import CarteraMergeService
from cobranzas.domain.services.manifiesto_lis_service import ManifiestoLisService


def build_proceso_chain(
    morosidad_repository: CreditoRepositoryPort,
    cartera_repository: CarteraRepositoryPort,
    reporte_repository: ReporteRepositoryPort,
    manifiesto_repository: ManifiestoRepositoryPort,
    cobranzas_service: CobranzasService,
    cartera_merge_service: CarteraMergeService,
    manifiesto_lis_service: ManifiestoLisService,
) -> Handler:
    """Cadena: morosidad -> cartera -> procesamiento (JSON + LIS)."""
    morosidad = LecturaMorosidadHandler(morosidad_repository)
    cartera = LecturaCarteraHandler(cartera_repository, cartera_merge_service)
    procesamiento = ProcesamientoMoraHandler(
        cobranzas_service,
        reporte_repository,
        manifiesto_repository,
        manifiesto_lis_service,
    )

    morosidad.enlazar(cartera).enlazar(procesamiento)
    return morosidad
