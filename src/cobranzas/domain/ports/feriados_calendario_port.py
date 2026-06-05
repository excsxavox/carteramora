from abc import ABC, abstractmethod
from datetime import date
from typing import Set


class FeriadosCalendarioPort(ABC):
    @abstractmethod
    def fechas_vigentes(self) -> Set[date]:
        """Fechas de feriado activas en catálogo."""
