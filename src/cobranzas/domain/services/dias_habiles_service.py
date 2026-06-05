"""Cálculo de días hábiles y vencimiento efectivo (HU mora temprana)."""

from calendar import monthrange
from datetime import date, timedelta
from typing import Set


def es_fin_de_semana(fecha: date) -> bool:
    return fecha.weekday() >= 5


def es_feriado(fecha: date, feriados: Set[date]) -> bool:
    return fecha in feriados


def es_dia_habil(fecha: date, feriados: Set[date]) -> bool:
    return not es_fin_de_semana(fecha) and not es_feriado(fecha, feriados)


def siguiente_dia_habil(fecha: date, feriados: Set[date]) -> date:
    """Mueve la fecha al primer día hábil en o después de `fecha`."""
    actual = fecha
    while not es_dia_habil(actual, feriados):
        actual += timedelta(days=1)
    return actual


def fecha_pago_nominal(anio: int, mes: int, dia_pago: int) -> date:
    ultimo_dia = monthrange(anio, mes)[1]
    return date(anio, mes, min(dia_pago, ultimo_dia))


def vencimiento_efectivo(anio: int, mes: int, dia_pago: int, feriados: Set[date]) -> date:
    """Día hábil en que vence el pago del mes (sáb/dom/feriado → siguiente hábil)."""
    nominal = fecha_pago_nominal(anio, mes, dia_pago)
    return siguiente_dia_habil(nominal, feriados)


def ultimo_vencimiento_hasta(
    fecha_corte: date, dia_pago: int, feriados: Set[date]
) -> date:
    """Último vencimiento efectivo de cuota en o antes de la fecha de corte."""
    candidatos = [
        vencimiento_efectivo(fecha_corte.year, fecha_corte.month, dia_pago, feriados),
        vencimiento_efectivo(
            fecha_corte.year - 1 if fecha_corte.month == 1 else fecha_corte.year,
            12 if fecha_corte.month == 1 else fecha_corte.month - 1,
            dia_pago,
            feriados,
        ),
    ]
    validos = [v for v in candidatos if v <= fecha_corte]
    if not validos:
        return min(candidatos)
    return max(validos)


def dias_mora_temprana(
    fecha_corte: date, dia_pago: int, feriados: Set[date]
) -> int:
    """
    Días de mora según día de pago y calendario hábil.
    Si el corte es el mismo día del vencimiento efectivo → 0.
    """
    if dia_pago <= 0:
        return 0
    vencimiento = ultimo_vencimiento_hasta(fecha_corte, dia_pago, feriados)
    if fecha_corte <= vencimiento:
        return 0
    return (fecha_corte - vencimiento).days
