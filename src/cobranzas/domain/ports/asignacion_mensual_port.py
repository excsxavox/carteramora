from abc import ABC, abstractmethod
from datetime import date
from typing import Dict, Optional, Tuple


class AsignacionMensualPort(ABC):
    @abstractmethod
    def asignaciones_del_mes(
        self, anio: int, mes: int
    ) -> Dict[str, Tuple[str, str]]:
        """
        Devuelve mapa numero_operacion -> (codigo_asesor, nombre_asesor)
        para asignaciones ya registradas en el mes.
        """
