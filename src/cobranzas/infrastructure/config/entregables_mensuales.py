"""Rutas de entregables HU-GRC-01 (carpeta única por mes)."""

from datetime import date
from pathlib import Path
from typing import Optional, Set

from cobranzas.domain.services.dias_habiles_service import fecha_consulta_mora
from cobranzas.infrastructure.config.fecha_corte import fecha_corte_mmddyyyy


def carpeta_entregables_mes(directorio_destino: Path, fecha: date) -> Path:
    """destino/{año}/{MM}/ — carpeta mensual de entregables."""
    return directorio_destino / str(fecha.year) / f"{fecha.month:02d}"


def ruta_acumulado_mensual(directorio_destino: Path, fecha: date) -> Path:
    """destino/{año}/{MM}/asignacion_acumulado_{YYYYMM}.xlsx"""
    carpeta = carpeta_entregables_mes(directorio_destino, fecha)
    return carpeta / f"asignacion_acumulado_{fecha.year}{fecha.month:02d}.xlsx"


def ruta_acumulado_fin_mes(directorio_destino: Path, fecha_proceso: date) -> Path:
    """destino/{año}/{MM}/acumulado_fin_mes_{MMDDYYYY}.xlsx (fecha = proceso efectivo)."""
    carpeta = carpeta_entregables_mes(directorio_destino, fecha_proceso)
    return carpeta / f"acumulado_fin_mes_{fecha_corte_mmddyyyy(fecha_proceso)}.xlsx"


def ruta_asignacion_mensual(directorio_destino: Path, fecha: date) -> Path:
    """destino/{año}/{MM}/ASIGNACION_{MMDDYYYY}.csv"""
    carpeta = carpeta_entregables_mes(directorio_destino, fecha)
    return carpeta / f"ASIGNACION_{fecha_corte_mmddyyyy(fecha)}.csv"


def ruta_asignacion_desde_fecha_archivo(
    directorio_destino: Path,
    fecha_archivo: date,
    feriados: Optional[Set[date]] = None,
) -> Path:
    """ASIGNACION con fecha de proceso (consulta efectiva al día hábil siguiente)."""
    fecha_proceso = fecha_consulta_mora(fecha_archivo, feriados or set())
    return ruta_asignacion_mensual(directorio_destino, fecha_proceso)
