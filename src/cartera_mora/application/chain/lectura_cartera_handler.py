import logging

from cartera_mora.application.chain.handler import Handler
from cartera_mora.application.chain.proceso_context import ProcesoContext
from cartera_mora.domain.ports.cartera_repository import CarteraRepositoryPort
from cartera_mora.domain.services.cartera_merge_service import CarteraMergeService

logger = logging.getLogger(__name__)


class LecturaCarteraHandler(Handler):
    """Paso 2: lee TE detallado de cartera y enriquece operaciones de morosidad."""

    def __init__(
        self,
        cartera_repository: CarteraRepositoryPort,
        merge_service: CarteraMergeService,
    ) -> None:
        super().__init__()
        self._cartera_repository = cartera_repository
        self._merge_service = merge_service

    def _procesar(self, contexto: ProcesoContext) -> ProcesoContext:
        creditos_cartera = self._cartera_repository.obtener_creditos()
        contexto.total_cartera_leidas = len(creditos_cartera)
        contexto.creditos = self._merge_service.enriquecer_con_cartera(
            contexto.creditos, creditos_cartera
        )
        contexto.total_enriquecidos = sum(
            1
            for c in contexto.creditos
            if c.cedula or c.calificacion or c.total_operacion
        )
        logger.info(
            "Cartera | operaciones_te=%s enriquecidas=%s",
            contexto.total_cartera_leidas,
            contexto.total_enriquecidos,
        )
        return contexto
