"""Calendario de asignación mensual (HU mora temprana)."""

from calendar import monthrange
from datetime import date


def es_primer_dia_mes(fecha_corte: date) -> bool:
    """True si es el día 1 del mes (ej. 06012026 en Postman = 01/06/2026)."""
    return fecha_corte.day == 1


def es_ultimo_dia_mes(fecha_corte: date) -> bool:
    """True si la fecha es el último día calendario del mes (ej. 30/06/2026)."""
    return fecha_corte.day == monthrange(fecha_corte.year, fecha_corte.month)[1]


def es_dia_solo_historial(fecha_corte: date) -> bool:
    """
    Solo persistir historial en BD: sin asignación ni ASIGNACION.csv.

    Aplica al último día del mes (cierre, ej. 06302026 en Postman).
    La reasignación al cambiar de mes la resuelve asignaciones_del_mes(año, mes).
    """
    return es_ultimo_dia_mes(fecha_corte)


def debe_asignar_asesores(fecha_corte: date) -> bool:
    return not es_dia_solo_historial(fecha_corte)


def debe_exportar_asignacion(fecha_corte: date) -> bool:
    return not es_dia_solo_historial(fecha_corte)
