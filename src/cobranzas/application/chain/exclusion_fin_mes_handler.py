import logging

from cobranzas.application.chain.handler import Handler
from cobranzas.application.chain.proceso_context import ProcesoContext
from cobranzas.domain.ports.operaciones_fin_mes_port import OperacionesFinMesPort

logger = logging.getLogger(__name__)


def _normalizar(numero: str) -> str:
    return (numero or "").strip()


class ExclusionFinMesHandler(Handler):
    """Excluye del proceso diario las operaciones ya capturadas en fin de mes.

    En un proceso normal (no fin de mes), toda operación cuyo número ya esté
    marcado como FIN_DE_MES en un corte anterior se elimina de ``creditos`` para
    que no entre a asignación, persistencia ni acumulado.
    """

    def __init__(self, operaciones_fin_mes: OperacionesFinMesPort) -> None:
        super().__init__()
        self._operaciones_fin_mes = operaciones_fin_mes

    def _procesar(self, contexto: ProcesoContext) -> ProcesoContext:
        if contexto.es_fin_de_mes or not contexto.creditos:
            return contexto

        fecha_corte = contexto.creditos[0].fecha_corte
        excluir = self._operaciones_fin_mes.operaciones_fin_de_mes(fecha_corte)
        if not excluir:
            return contexto

        antes = len(contexto.creditos)
        contexto.creditos = [
            c for c in contexto.creditos if _normalizar(c.id_credito) not in excluir
        ]
        quitadas = antes - len(contexto.creditos)
        if quitadas:
            logger.info(
                "Exclusión fin de mes | %s | operaciones quitadas=%s (ya capturadas en cierre)",
                fecha_corte.isoformat(),
                quitadas,
            )
        return contexto
