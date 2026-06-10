"""Rutas de entregables HU-GRC-01 (carpeta única por mes)."""

from datetime import date
from pathlib import Path

from cobranzas.infrastructure.config.fecha_corte import fecha_corte_mmddyyyy


def carpeta_entregables_mes(directorio_destino: Path, fecha: date) -> Path:
    """destino/{año}/{MM}/ — carpeta mensual de entregables."""
    return directorio_destino / str(fecha.year) / f"{fecha.month:02d}"


def ruta_acumulado_mensual(directorio_destino: Path, fecha: date) -> Path:
    """destino/{año}/{MM}/asignacion_acumulado_{YYYYMM}.xlsx"""
    carpeta = carpeta_entregables_mes(directorio_destino, fecha)
    return carpeta / f"asignacion_acumulado_{fecha.year}{fecha.month:02d}.xlsx"


def ruta_asignacion_mensual(directorio_destino: Path, fecha: date) -> Path:
    """destino/{año}/{MM}/ASIGNACION_{MMDDYYYY}.csv"""
    carpeta = carpeta_entregables_mes(directorio_destino, fecha)
    return carpeta / f"ASIGNACION_{fecha_corte_mmddyyyy(fecha)}.csv"
