from abc import ABC, abstractmethod


class ManifiestoRepositoryPort(ABC):
    """Puerto de salida: persiste el manifiesto .lis de la ejecución."""

    @abstractmethod
    def guardar_manifiesto(self, contenido: str) -> None:
        raise NotImplementedError
