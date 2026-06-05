from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class AsignacionCredito:
    fecha_corte: date
    numero_operacion: str
    identificacion: str
    socio: str
    nombre: str
    saldo_capital: float
    dias_mora: int
    codigo_asesor: str
    nombre_asesor: str
    id_credito_recblue: str = ""
    reasignado: bool = False
