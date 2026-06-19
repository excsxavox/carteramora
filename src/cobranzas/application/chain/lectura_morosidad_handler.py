import logging

from cobranzas.application.chain.handler import Handler
from cobranzas.application.chain.proceso_context import ProcesoContext
from cobranzas.domain.ports.credito_repository import CreditoRepositoryPort

logger = logging.getLogger(__name__)


class LecturaMorosidadHandler(Handler):
    """Paso 1: lee el Cuadro de Morosidad Consolidado."""

    def __init__(self, morosidad_repository: CreditoRepositoryPort) -> None:
        super().__init__()
        self._morosidad_repository = morosidad_repository

    def _procesar(self, contexto: ProcesoContext) -> ProcesoContext:
        if contexto.es_fin_de_mes:
            contexto.creditos = []
            contexto.creditos_morosidad = []
            contexto.columnas_morosidad = ()
            logger.info(
                "Fin de mes | CAMOROSICO omitido (solo se lee CADETACACO)"
            )
            return contexto

        creditos = self._morosidad_repository.obtener_creditos()
        contexto.creditos = creditos
        contexto.creditos_morosidad = list(creditos)
        contexto.columnas_morosidad = (
            creditos[0].columnas_tab() if creditos else ()
        )
        logger.info("Morosidad | operaciones_cargadas=%s", len(creditos))
        return contexto
