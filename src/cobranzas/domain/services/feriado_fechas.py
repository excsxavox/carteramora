"""Utilidades de fechas para catálogo de feriados (formato Excel M/D/Y)."""

from datetime import date, datetime, timedelta
from typing import Optional


def parsear_fecha_excel(valor) -> Optional[date]:
    """Interpreta fechas del Excel como mes/día/año (p. ej. 12/25/2026)."""
    if valor is None:
        return None

    if isinstance(valor, datetime):
        return valor.date()

    if isinstance(valor, date):
        return valor

    texto = str(valor).strip()
    if not texto:
        return None

    for formato in ("%m/%d/%Y", "%m-%d-%Y", "%m/%d/%y", "%m-%d-%y"):
        try:
            return datetime.strptime(texto[:10], formato).date()
        except ValueError:
            continue

    return None


def parsear_fecha_catalogo(valor) -> Optional[date]:
    """Interpreta valor guardado en catalogo (YYYY-MM-DD u otros)."""
    if valor is None:
        return None

    if isinstance(valor, datetime):
        return valor.date()

    if isinstance(valor, date):
        return valor

    texto = str(valor).strip()
    if not texto:
        return None

    for formato in (
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%m-%d-%Y",
        "%m/%d/%y",
        "%m-%d-%y",
    ):
        try:
            return datetime.strptime(texto[:10], formato).date()
        except ValueError:
            continue

    return None


def rango_dias(fecha_inicio: date, fecha_fin: date) -> list[date]:
    dias: list[date] = []
    actual = fecha_inicio
    while actual <= fecha_fin:
        dias.append(actual)
        actual += timedelta(days=1)
    return dias


def fecha_a_valor_catalogo(fecha: date) -> str:
    return fecha.strftime("%Y-%m-%d")
