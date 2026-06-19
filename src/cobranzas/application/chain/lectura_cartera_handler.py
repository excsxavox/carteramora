import logging

from cobranzas.application.chain.handler import Handler
from cobranzas.application.chain.proceso_context import ProcesoContext
from cobranzas.domain.ports.cartera_repository import CarteraRepositoryPort
from cobranzas.domain.services.cartera_merge_service import CarteraMergeService

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
        contexto.columnas_cartera = (
            creditos_cartera[0].columnas_tab() if creditos_cartera else ()
        )

        if contexto.es_fin_de_mes:
            contexto.creditos = creditos_cartera
            contexto.total_enriquecidos = len(creditos_cartera)
            logger.info(
                "Fin de mes | base=CADETACACO | operaciones=%s (sin merge CAMOROSICO)",
                len(creditos_cartera),
            )
            return contexto

        ops_morosidad = {c.id_credito.strip() for c in contexto.creditos}
        ops_cartera = {c.id_credito.strip() for c in creditos_cartera}
        en_ambos = ops_morosidad & ops_cartera
        solo_morosidad = ops_morosidad - ops_cartera
        solo_cartera = ops_cartera - ops_morosidad
        logger.info(
            "Cobertura archivos | CAMOROSICO=%s | CADETACACO=%s | en_ambos=%s | "
            "solo_CAMOROSICO=%s | solo_CADETACACO(no_en_acumulado)=%s",
            len(ops_morosidad),
            len(ops_cartera),
            len(en_ambos),
            len(solo_morosidad),
            len(solo_cartera),
        )

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
