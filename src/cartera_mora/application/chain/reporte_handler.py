import logging

from cartera_mora.application.chain.handler import Handler
from cartera_mora.application.chain.proceso_context import ProcesoContext
from cartera_mora.domain.ports.manifiesto_repository import ManifiestoRepositoryPort
from cartera_mora.domain.ports.reporte_repository import ReporteRepositoryPort
from cartera_mora.domain.services.cartera_mora_service import CarteraMoraService
from cartera_mora.domain.services.manifiesto_lis_service import ManifiestoLisService

logger = logging.getLogger(__name__)


class ProcesamientoMoraHandler(Handler):
    """Paso 3: filtra mora, genera reporte JSON y manifiesto .lis."""

    def __init__(
        self,
        cartera_mora_service: CarteraMoraService,
        reporte_repository: ReporteRepositoryPort,
        manifiesto_repository: ManifiestoRepositoryPort,
        manifiesto_lis_service: ManifiestoLisService,
    ) -> None:
        super().__init__()
        self._service = cartera_mora_service
        self._reporte_repository = reporte_repository
        self._manifiesto_repository = manifiesto_repository
        self._manifiesto_lis_service = manifiesto_lis_service

    def _procesar(self, contexto: ProcesoContext) -> ProcesoContext:
        creditos_mora = self._service.filtrar_en_mora(
            contexto.creditos, contexto.dias_mora_minimo
        )
        contexto.creditos_mora = creditos_mora

        reporte = self._service.construir_reporte(creditos_mora, contexto.dias_mora_minimo)
        self._reporte_repository.guardar_reporte(reporte)
        contexto.reporte = reporte

        contenido_lis = self._manifiesto_lis_service.construir(
            archivo_morosidad=contexto.archivo_morosidad,
            archivo_cartera=contexto.archivo_cartera,
            archivo_reporte=contexto.archivo_reporte,
            archivo_lis=contexto.archivo_lis,
            creditos_morosidad=contexto.creditos_morosidad,
            total_cartera_leidas=contexto.total_cartera_leidas,
            total_enriquecidos=contexto.total_enriquecidos,
            creditos_mora=creditos_mora,
            reporte=reporte,
        )
        self._manifiesto_repository.guardar_manifiesto(contenido_lis)

        logger.info(
            "Procesamiento | en_mora=%s saldo=%.2f | lis=%s",
            reporte["total_creditos"],
            reporte["total_saldo_mora"],
            contexto.archivo_lis,
        )
        return contexto
