from datetime import date

from cobranzas.domain.services.asignacion_calendario import (
    debe_asignar_asesores,
    debe_exportar_asignacion,
    es_dia_solo_historial,
    es_ultimo_dia_mes,
)


def test_06302026_ultimo_dia_junio_solo_historial():
    """Postman 06302026 = 30/06/2026: sin asignación, solo subir información."""
    corte = date(2026, 6, 30)
    assert es_ultimo_dia_mes(corte)
    assert es_dia_solo_historial(corte)
    assert not debe_asignar_asesores(corte)
    assert not debe_exportar_asignacion(corte)


def test_07012026_primer_dia_julio_permite_asignacion():
    """Postman 07012026 = 01/07/2026: asigna si aún no hay registros del mes en BD."""
    corte = date(2026, 7, 1)
    assert not es_ultimo_dia_mes(corte)
    assert not es_dia_solo_historial(corte)
    assert debe_asignar_asesores(corte)
    assert debe_exportar_asignacion(corte)


def test_dia_intermedio_lógica_normal():
    corte = date(2026, 4, 6)
    assert not es_dia_solo_historial(corte)
    assert debe_asignar_asesores(corte)
    assert debe_exportar_asignacion(corte)


def test_febrero_ultimo_dia_bisiesto():
    corte = date(2024, 2, 29)
    assert es_ultimo_dia_mes(corte)
    assert es_dia_solo_historial(corte)
