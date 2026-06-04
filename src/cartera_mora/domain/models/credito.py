from dataclasses import dataclass
from datetime import date
from enum import Enum


class EstadoMora(str, Enum):
    AL_DIA = "al_dia"
    MORA_LEVE = "mora_leve"
    MORA_GRAVE = "mora_grave"


@dataclass(frozen=True)
class Credito:
    """Entidad unificada desde Cuadro de Morosidad y TE Detallado de Cartera."""

    id_credito: str
    cliente: str
    saldo_pendiente: float
    dias_mora: int
    fecha_corte: date
    estado_operacion: str = ""
    socio: str = ""
    oficina: str = ""
    nombre_oficial: str = ""
    tipo_operacion: str = ""
    total_atrasado: float = 0.0
    cedula: str = ""
    calificacion: str = ""
    total_operacion: float = 0.0
    segmentacion: str = ""
    fuente_repago: str = ""
    codigo_oficial: str = ""

    def clasificar_mora(self, dias_mora_minimo: int) -> EstadoMora:
        if self.dias_mora < dias_mora_minimo:
            return EstadoMora.AL_DIA
        if self.dias_mora < 90:
            return EstadoMora.MORA_LEVE
        return EstadoMora.MORA_GRAVE

    def esta_en_mora(self, dias_mora_minimo: int) -> bool:
        return self.clasificar_mora(dias_mora_minimo) != EstadoMora.AL_DIA
