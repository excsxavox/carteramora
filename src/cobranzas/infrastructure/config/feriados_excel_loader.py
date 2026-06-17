"""Carga feriados desde Excel de catálogo (sin BD)."""

from datetime import date
from typing import Set

from cobranzas.domain.services.feriado_fechas import rango_dias
from cobranzas.infrastructure.adapters.excel_feriado_reader import ExcelFeriadoReader
from cobranzas.infrastructure.config.settings import Settings


def cargar_feriados_desde_excel(settings: Settings) -> Set[date]:
    reader = ExcelFeriadoReader()
    archivo = reader.buscar_archivo(
        settings.directorio_excel_feriados, settings.patron_excel_feriados
    )
    if archivo is None:
        return set()

    fechas: Set[date] = set()
    for rango in reader.leer_feriados(archivo):
        fechas.update(rango_dias(rango.fecha_inicio, rango.fecha_fin))
    return fechas
