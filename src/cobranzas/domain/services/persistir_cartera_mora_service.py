from datetime import datetime, timezone
from typing import List

from cobranzas.domain.models.credito import Credito
from cobranzas.domain.ports.cobranza_db_repository import CobranzaDbRepositoryPort


class PersistirCarteraMoraService:
    """Orquesta la persistencia de créditos en mora hacia la base de datos."""

    def __init__(
        self,
        repository: CobranzaDbRepositoryPort,
        dias_mora_minimo: int = 30,
    ) -> None:
        self._repository = repository
        self._dias_mora_minimo = dias_mora_minimo

    def persistir(self, creditos_mora: List[Credito]) -> int:
        if not creditos_mora:
            return 0
        return self._repository.guardar_creditos_mora(creditos_mora)

    @staticmethod
    def ahora_utc() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)
