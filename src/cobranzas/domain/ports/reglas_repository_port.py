from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class ReglaNegocio:
    tipo: str
    valor: str
    prioridad: int = 0
    nombre: Optional[str] = None


class ReglasRepositoryPort(ABC):
    @abstractmethod
    def contar_reglas(self) -> int:
        """Total de filas en reglas."""

    @abstractmethod
    def listar_activas_por_tipos(self, tipos: frozenset[str]) -> List[ReglaNegocio]:
        """Reglas activas de los tipos indicados, orden prioridad DESC."""

    @abstractmethod
    def insertar_reglas(self, reglas: List[ReglaNegocio]) -> int:
        """Inserta reglas nuevas; retorna cantidad insertada."""

    @abstractmethod
    def actualizar_valor_por_tipo(self, tipo: str, valor: str) -> int:
        """Actualiza valor de reglas activas del tipo; retorna filas afectadas."""
