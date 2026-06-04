from abc import ABC, abstractmethod

from cartera_mora.domain.models.credito import Credito


class CreditoRepositoryPort(ABC):
    """Puerto de salida: obtiene créditos desde una fuente externa."""

    @abstractmethod
    def obtener_creditos(self) -> list[Credito]:
        raise NotImplementedError
