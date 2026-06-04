import logging

from cartera_mora.application.chain.handler import Handler
from cartera_mora.application.chain.proceso_context import ProcesoContext
from cartera_mora.domain.ports.credito_repository import CreditoRepositoryPort

logger = logging.getLogger(__name__)


class LecturaMorosidadHandler(Handler):
    """Paso 1: lee el Cuadro de Morosidad Consolidado."""

    def __init__(self, morosidad_repository: CreditoRepositoryPort) -> None:
        super().__init__()
        self._morosidad_repository = morosidad_repository

    def _procesar(self, contexto: ProcesoContext) -> ProcesoContext:
        creditos = self._morosidad_repository.obtener_creditos()
        contexto.creditos = creditos
        contexto.creditos_morosidad = list(creditos)
        logger.info("Morosidad | operaciones_cargadas=%s", len(creditos))
        return contexto
