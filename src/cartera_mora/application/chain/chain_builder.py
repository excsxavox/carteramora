from cartera_mora.application.chain.handler import Handler
from cartera_mora.application.chain.lectura_cartera_handler import LecturaCarteraHandler
from cartera_mora.application.chain.lectura_morosidad_handler import LecturaMorosidadHandler
from cartera_mora.application.chain.reporte_handler import ProcesamientoMoraHandler
from cartera_mora.domain.ports.cartera_repository import CarteraRepositoryPort
from cartera_mora.domain.ports.credito_repository import CreditoRepositoryPort
from cartera_mora.domain.ports.manifiesto_repository import ManifiestoRepositoryPort
from cartera_mora.domain.ports.reporte_repository import ReporteRepositoryPort
from cartera_mora.domain.services.cartera_mora_service import CarteraMoraService
from cartera_mora.domain.services.cartera_merge_service import CarteraMergeService
from cartera_mora.domain.services.manifiesto_lis_service import ManifiestoLisService


def build_proceso_chain(
    morosidad_repository: CreditoRepositoryPort,
    cartera_repository: CarteraRepositoryPort,
    reporte_repository: ReporteRepositoryPort,
    manifiesto_repository: ManifiestoRepositoryPort,
    cartera_mora_service: CarteraMoraService,
    cartera_merge_service: CarteraMergeService,
    manifiesto_lis_service: ManifiestoLisService,
) -> Handler:
    """Cadena: morosidad -> cartera -> procesamiento (JSON + LIS)."""
    morosidad = LecturaMorosidadHandler(morosidad_repository)
    cartera = LecturaCarteraHandler(cartera_repository, cartera_merge_service)
    procesamiento = ProcesamientoMoraHandler(
        cartera_mora_service,
        reporte_repository,
        manifiesto_repository,
        manifiesto_lis_service,
    )

    morosidad.enlazar(cartera).enlazar(procesamiento)
    return morosidad
