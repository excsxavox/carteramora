"""Fila del Excel acumulado fin de mes (campos deudores + deuda)."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class FilaAcumuladoFinMes:
    fecha_proceso: date
    deudores_nombre: str
    deudores_documento: str
    deudores_socio: str
    numero_operacion: str
    fecha_corte: Optional[date]
    archivo_origen: str
    oficina: str
    desc_oficina: str
    socio: str
    nombre: str
    cedula: str
    sector: str
    tipo_operacion: str
    tipo_destino: str
    fecha_concesion: Optional[date]
    fecha_vencimiento: Optional[date]
    fecha_ultimo_pago: Optional[date]
    valor_original_prestamo: Optional[Decimal]
    saldo_capital_prestamo: Optional[Decimal]
    calificacion: str
    total_provision: Optional[Decimal]
    saldo_140x: Optional[Decimal]
    saldo_141x: Optional[Decimal]
    saldo_142x: Optional[Decimal]
    interes_normal: Optional[Decimal]
    interes_devengado: Optional[Decimal]
    interes_vencido: Optional[Decimal]
    interes_resolucion: Optional[Decimal]
    interes_castigado: Optional[Decimal]
    interes_mora: Optional[Decimal]
    otros_rubros_deuda: Optional[Decimal]
    total_operacion: Optional[Decimal]
    estado: str
    oficial: str
    dias_mora: Optional[int]
    dias_atraso_camorosico: Optional[int]
    fecha_ingreso: Optional[date]
    tipo: str
    dia_pago: Optional[int]
    valor_cuota: Optional[Decimal]
    cuota_actual: Optional[int]
    dividendos: Optional[int]
    cod_oficial_asignado: str
    oficial_asignado: str
    cod_oficial_adm: str
    oficial_adm: str
    operacion_homologada: str
    decision: str
    segmentacion: str
    score: str
    fuente_repago: str
    identificacion_ifi: str
    actividad_economica: str
    fecha_archivo: Optional[date]
    tipo_mes: str
    tipo_fideicomiso: str
    proceso_cod: Optional[int]
    estado_mora: str
    id_credito_recblue: str
