from datetime import date, timedelta

from cobranzas.domain.services.dias_habiles_service import (
    calcular_cuota_mora,
    contar_dias_mora_habiles,
    dias_mora_temprana,
    siguiente_dia_habil,
    vencimiento_efectivo,
)


def test_sabado_30_mueve_vencimiento_a_lunes():
    feriados: set[date] = set()
    venc = vencimiento_efectivo(2026, 5, 30, feriados)
    assert venc.weekday() == 0  # lunes 1-jun-2026 (30-may-2026 es s?bado)


def test_mora_un_dia_despues_del_vencimiento_habil():
    feriados: set[date] = set()
    venc = vencimiento_efectivo(2026, 5, 30, feriados)
    assert dias_mora_temprana(venc, 30, feriados) == 0
    martes = venc + timedelta(days=1)
    resultado = calcular_cuota_mora(martes, 30, feriados)
    assert resultado.clasificacion == "mora_temprana"
    assert resultado.dias == 1


def test_mora_temprana_solo_cuota_del_mes_de_corte():
    feriados: set[date] = set()
    corte = date(2026, 6, 20)
    resultado = calcular_cuota_mora(corte, 15, feriados)
    assert resultado.clasificacion == "mora_temprana"
    assert resultado.mes_cuota == 6
    assert resultado.dias == 4
    assert dias_mora_temprana(corte, 15, feriados) == 4


def test_mes_anterior_impago_no_cuenta_solo_mes_consulta():
    """Mora temprana: solo cuota del mes de corte (abril a?n no vence el 6-abr)."""
    feriados: set[date] = set()
    corte = date(2026, 4, 6)
    resultado = calcular_cuota_mora(corte, 24, feriados)
    assert resultado.clasificacion == "al_dia"
    assert resultado.mes_cuota == 4
    assert resultado.dias == 0


def test_pago_mes_anterior_no_cubre_mes_consulta():
    feriados: set[date] = set()
    corte = date(2026, 5, 6)
    resultado = calcular_cuota_mora(
        corte, 5, feriados, ultimo_pago=date(2026, 4, 30)
    )
    assert resultado.clasificacion == "mora_temprana"
    assert resultado.mes_cuota == 5
    assert resultado.dias == 1


def test_pago_mismo_dia_vencimiento_mes_consulta_sigue_en_mora():
    feriados: set[date] = set()
    corte = date(2026, 5, 6)
    resultado = calcular_cuota_mora(
        corte, 5, feriados, ultimo_pago=date(2026, 5, 5)
    )
    assert resultado.clasificacion == "mora_temprana"
    assert resultado.dias == 1


def test_pago_despues_vencimiento_mes_consulta_al_dia():
    feriados: set[date] = set()
    corte = date(2026, 5, 6)
    resultado = calcular_cuota_mora(
        corte, 5, feriados, ultimo_pago=date(2026, 5, 6)
    )
    assert resultado.clasificacion == "al_dia"
    assert resultado.dias == 0


def test_dias_mora_excluye_fin_de_semana():
    feriados: set[date] = set()
    venc = date(2026, 6, 5)  # viernes
    corte = date(2026, 6, 8)  # lunes
    assert contar_dias_mora_habiles(venc, corte, feriados) == 1


def test_dias_mora_excluye_feriado_en_periodo():
    feriados = {date(2026, 6, 17)}
    venc = date(2026, 6, 15)
    corte = date(2026, 6, 19)
    assert contar_dias_mora_habiles(venc, corte, feriados) == 3


def test_feriado_mueve_vencimiento():
    feriados = {date(2026, 6, 1)}
    nominal = date(2026, 6, 1)
    assert siguiente_dia_habil(nominal, feriados) == date(2026, 6, 2)


def test_ultimo_pago_marzo_excluye_mora_en_abril():
    feriados: set[date] = set()
    corte = date(2026, 4, 6)
    resultado = calcular_cuota_mora(
        corte, 30, feriados, ultimo_pago=date(2026, 3, 30)
    )
    assert resultado.clasificacion == "al_dia"
    assert resultado.dias == 0


def test_ultimo_pago_posterior_al_corte_no_cuenta():
    feriados: set[date] = set()
    corte = date(2026, 4, 6)
    resultado = calcular_cuota_mora(
        corte, 30, feriados, ultimo_pago=date(2026, 5, 19)
    )
    assert resultado.clasificacion == "al_dia"
    assert resultado.mes_cuota == 4
    assert resultado.dias == 0
