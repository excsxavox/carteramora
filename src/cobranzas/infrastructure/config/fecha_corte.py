"""Normalización de fecha de corte para rutas y API (MMDDYYYY)."""

from datetime import date, datetime
from typing import Optional

FORMATO_FECHA_CARPETA = "%m%d%Y"


def fecha_corte_mmddyyyy(fecha: Optional[date] = None) -> str:
    """Fecha de corte en formato MMDDYYYY (ej. 05052026 = 5 mayo 2026)."""
    return (fecha or date.today()).strftime(FORMATO_FECHA_CARPETA)


def parsear_fecha_corte(texto: str) -> date:
    texto = (texto or "").strip()
    if len(texto) != 8 or not texto.isdigit():
        raise ValueError(f"FECHA_CORTE inválida (use MMDDYYYY): {texto!r}")
    return datetime.strptime(texto, FORMATO_FECHA_CARPETA).date()


def normalizar_fecha_corte(texto: str) -> str:
    """
    Acepta MMDDYYYY (05052026) o ISO YYYY-MM-DD y devuelve MMDDYYYY.
    """
    valor = (texto or "").strip()
    if not valor:
        raise ValueError("La fecha es obligatoria")

    if len(valor) == 8 and valor.isdigit():
        datetime.strptime(valor, FORMATO_FECHA_CARPETA)
        return valor

    for formato in ("%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y"):
        try:
            return datetime.strptime(valor[:10], formato).date().strftime(
                FORMATO_FECHA_CARPETA
            )
        except ValueError:
            continue

    raise ValueError(
        f"Formato de fecha no válido: {texto!r}. Use MMDDYYYY o YYYY-MM-DD."
    )


def fecha_corte_desde_texto(texto: str) -> date:
    return parsear_fecha_corte(normalizar_fecha_corte(texto))
