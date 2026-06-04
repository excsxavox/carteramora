import logging

from cobranzas.application.chain.handler import Handler
from cobranzas.application.chain.proceso_context import ProcesoContext
from cobranzas.domain.services.persistir_cartera_mora_service import (
    PersistirCarteraMoraService,
)

logger = logging.getLogger(__name__)


class PersistenciaBDHandler(Handler):
    """Paso opcional: guarda créditos en mora en BD_Cobranza (SQLite/SQL Server)."""

    def __init__(self, persistir_service: PersistirCarteraMoraService) -> None:
        super().__init__()
        self._persistir_service = persistir_service

    def _procesar(self, contexto: ProcesoContext) -> ProcesoContext:
        if not contexto.persistir_en_bd:
            return contexto
        guardados = self._persistir_service.persistir(contexto.creditos_mora)
        contexto.registros_persistidos_bd = guardados
        logger.info(
            "BD | creditos=%s | tablas=deudores,deuda,asesores,asesores_deuda,catalogo | url=%s",
            guardados,
            contexto.database_url,
        )
        return contexto
