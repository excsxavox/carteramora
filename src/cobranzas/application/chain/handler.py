from abc import ABC, abstractmethod
from typing import Optional

from cobranzas.application.chain.proceso_context import ProcesoContext


class Handler(ABC):
    """Eslabón base de la cadena de responsabilidad."""

    def __init__(self, siguiente: Optional["Handler"] = None) -> None:
        self._siguiente = siguiente

    def enlazar(self, siguiente: "Handler") -> "Handler":
        self._siguiente = siguiente
        return siguiente

    def manejar(self, contexto: ProcesoContext) -> ProcesoContext:
        contexto = self._procesar(contexto)
        if self._siguiente is not None:
            return self._siguiente.manejar(contexto)
        return contexto

    @abstractmethod
    def _procesar(self, contexto: ProcesoContext) -> ProcesoContext:
        raise NotImplementedError
