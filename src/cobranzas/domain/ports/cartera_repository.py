from abc import ABC, abstractmethod

from cobranzas.domain.models.credito import Credito


class CarteraRepositoryPort(ABC):
    """Puerto de salida: obtiene operaciones del TE detallado de cartera."""

    @abstractmethod
    def obtener_creditos(self) -> list[Credito]:
        raise NotImplementedError
