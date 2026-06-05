from datetime import date, timedelta

from cobranzas.domain.services.dias_habiles_service import (
    calcular_cuota_mora,
    dias_mora_temprana,
    siguiente_dia_habil,
    vencimiento_efectivo,
)


def test_sabado_30_mueve_vencimiento_a_lunes():
    feriados: set[date] = set()
    venc = vencimiento_efectivo(2026, 5, 30, feriados)
    assert venc.weekday() == 0  # lunes 1-jun-2026 (30-may-2026 es sábado)


def test_mora_un_dia_despues_del_vencimiento_habil():
    feriados: set[date] = set()
    venc = vencimiento_efectivo(2026, 5, 30, feriados)
    assert dias_mora_temprana(venc, 30, feriados) == 0
    martes = venc + timedelta(days=1)
    # Cuota de mayo impaga en junio ? mora madura, no temprana
    assert dias_mora_temprana(martes, 30, feriados) == 0
    resultado = calcular_cuota_mora(martes, 30, feriados)
    assert resultado.clasificacion == "mora_madura"
    assert resultado.dias == 1


def test_mora_temprana_solo_cuota_del_mes_de_corte():
    feriados: set[date] = set()
    corte = date(2026, 6, 20)
    resultado = calcular_cuota_mora(corte, 15, feriados)
    assert resultado.clasificacion == "mora_temprana"
    assert resultado.mes_cuota == 6
    assert resultado.dias == 5
    assert dias_mora_temprana(corte, 15, feriados) == 5


def test_cuota_mes_anterior_es_mora_madura():
    feriados: set[date] = set()
    corte = date(2026, 4, 6)
    resultado = calcular_cuota_mora(corte, 24, feriados)
    assert resultado.clasificacion == "mora_madura"
    assert resultado.mes_cuota == 3
    assert resultado.dias == 13
    assert dias_mora_temprana(corte, 24, feriados) == 0


def test_feriado_mueve_vencimiento():
    feriados = {date(2026, 6, 1)}
    nominal = date(2026, 6, 1)
    assert siguiente_dia_habil(nominal, feriados) == date(2026, 6, 2)
