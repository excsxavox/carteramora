from abc import ABC, abstractmethod
from datetime import date
from typing import Dict, Optional, Tuple


class AsignacionMensualPort(ABC):
    @abstractmethod
    def asignaciones_del_mes(
        self, anio: int, mes: int, excluir_fecha: Optional[date] = None
    ) -> Dict[str, Tuple[str, str]]:
        """
        Mapa numero_operacion -> (codigo_asesor, nombre_asesor) ya asignados
        en el mes calendario (mora temprana). Días 2+ solo rotan los que faltan.

        Si se pasa ``excluir_fecha`` se omiten las asignaciones de ese corte
        (útil al re-procesar un corte: su propia asignación previa no debe
        contar como conservada).
        """
