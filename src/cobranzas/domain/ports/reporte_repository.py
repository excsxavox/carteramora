from abc import ABC, abstractmethod
from typing import Any


class ReporteRepositoryPort(ABC):
    """Puerto de salida: persiste el reporte de cartera en mora."""

    @abstractmethod
    def guardar_reporte(self, reporte: dict[str, Any]) -> None:
        raise NotImplementedError
