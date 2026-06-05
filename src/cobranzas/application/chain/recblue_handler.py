import logging
from dataclasses import replace

from cobranzas.application.chain.handler import Handler
from cobranzas.application.chain.proceso_context import ProcesoContext
from cobranzas.infrastructure.adapters.recblue_archivo_adapter import RecblueArchivoAdapter

logger = logging.getLogger(__name__)


class RecblueValidacionHandler(Handler):
    """Valida export Recblue (Excel/CSV) antes de mora temprana."""

    def __init__(self, recblue: RecblueArchivoAdapter) -> None:
        super().__init__()
        self._recblue = recblue

    def _procesar(self, contexto: ProcesoContext) -> ProcesoContext:
        if not contexto.validar_recblue:
            return contexto

        mapa = self._recblue.id_credito_por_operacion()
        contexto.mapa_recblue = mapa

        if self._recblue.errores_validacion:
            for error in self._recblue.errores_validacion:
                logger.error("Recblue: %s", error)
            contexto.errores_recblue = list(self._recblue.errores_validacion)
            return contexto

        if not mapa:
            logger.warning(
                "Recblue configurado pero sin registros útiles: %s",
                contexto.archivo_recblue,
            )
        else:
            logger.info(
                "Recblue validado | operaciones=%s | %s",
                len(mapa),
                contexto.archivo_recblue,
            )
        return contexto


class RecblueEnriquecimientoHandler(Handler):
    """Completa id_credito_recblue en créditos en mora antes de persistir."""

    def __init__(self, recblue: RecblueArchivoAdapter) -> None:
        super().__init__()
        self._recblue = recblue

    def _procesar(self, contexto: ProcesoContext) -> ProcesoContext:
        mapa = contexto.mapa_recblue or self._recblue.id_credito_por_operacion()
        if not mapa:
            return contexto

        contexto.creditos_mora = self._enriquecer(contexto.creditos_mora, mapa)
        sin_id = sum(1 for c in contexto.creditos_mora if not c.id_credito_recblue)
        if sin_id:
            logger.warning(
                "Recblue: %s operaciones en mora sin ID Crédito en export",
                sin_id,
            )
        return contexto

    @staticmethod
    def _enriquecer(creditos, mapa):
        resultado = []
        for credito in creditos:
            id_rb = (credito.id_credito_recblue or mapa.get(credito.id_credito, "")).strip()
            if id_rb and id_rb != credito.id_credito_recblue:
                resultado.append(replace(credito, id_credito_recblue=id_rb))
            else:
                resultado.append(credito)
        return resultado
