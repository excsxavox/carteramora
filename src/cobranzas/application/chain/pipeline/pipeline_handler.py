from abc import ABC, abstractmethod
from typing import Optional

from cobranzas.application.chain.pipeline.pipeline_context import PipelineContext


class PipelineHandler(ABC):
    """Eslabón de la cadena del pipeline (asesores → feriados → limpieza)."""

    def __init__(self, siguiente: Optional["PipelineHandler"] = None) -> None:
        self._siguiente = siguiente

    def enlazar(self, siguiente: "PipelineHandler") -> "PipelineHandler":
        self._siguiente = siguiente
        return siguiente

    def manejar(self, contexto: PipelineContext) -> PipelineContext:
        if contexto.detener:
            return contexto
        contexto = self._procesar(contexto)
        if contexto.detener or self._siguiente is None:
            return contexto
        return self._siguiente.manejar(contexto)

    @abstractmethod
    def _procesar(self, contexto: PipelineContext) -> PipelineContext:
        raise NotImplementedError
