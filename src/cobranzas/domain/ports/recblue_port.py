from abc import ABC, abstractmethod
from typing import Dict


class RecbluePort(ABC):
    @abstractmethod
    def id_credito_por_operacion(self) -> Dict[str, str]:
        """Mapa numero_operacion -> id_credito Recblue."""
