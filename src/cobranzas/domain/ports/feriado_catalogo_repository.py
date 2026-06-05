from abc import ABC, abstractmethod
from datetime import date

from dataclasses import dataclass


@dataclass
class FeriadoSincronizadoDetalle:
    insertados: int = 0
    activados: int = 0
    desactivados: int = 0


class FeriadoCatalogoRepositoryPort(ABC):
    @abstractmethod
    def obtener_o_crear_clave(self, clave: str) -> int:
        """Obtiene id_clave para feriados_catalogo (la crea si no existe)."""

    @abstractmethod
    def sincronizar_rango(
        self,
        id_clave: int,
        descripcion: str,
        fecha_inicio: date,
        fecha_fin: date,
    ) -> FeriadoSincronizadoDetalle:
        """Inserta, activa o desactiva días en dbo.catalogo según el Excel."""
