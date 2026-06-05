from abc import ABC, abstractmethod
from typing import List, Tuple


class AsesoresRotacionPort(ABC):
    """Asesores activos para rotación de mora temprana (código USUARIO, nombre)."""

    @abstractmethod
    def listar_activos(self) -> List[Tuple[str, str]]:
        """Retorna lista de (codigo_usuario, nombre) en orden estable."""
