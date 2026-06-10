"""Fila del Excel acumulado mensual (deuda + asignación)."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class FilaAcumuladoMensual:
    fecha_proceso: date
    desc_oficina: str
    nombre: str
    cedula: str
    operacion: str
    tipo_oper: str
    fecha_concesion: Optional[date]
    valor_ori_prestamo: Optional[Decimal]
    saldo_cap_prest: Optional[Decimal]
    calificac: str
    total_provision: Optional[Decimal]
    saldo_140x: Optional[Decimal]
    saldo_141x: Optional[Decimal]
    saldo_142x: Optional[Decimal]
    total_op: Optional[Decimal]
    est: str
    estado_mora: str
    dias_atraso_camorosico: Optional[int]
    dias_mora: Optional[int]
    tipo: str
    dia_pago: Optional[int]
    valor_cuota: Optional[Decimal]
    cuota_act: Optional[int]
    dividendos: Optional[int]
    oficial_adm: str
    decision: str
    segmentacion: str
    score: str
    fuente_repago: str
    identificacion_ifi: str
    usuario_asesor: str
    nombre_asesor: str
    id_credito_recblue: str
