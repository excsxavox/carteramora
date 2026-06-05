from datetime import date

from cobranzas.domain.services.dias_habiles_service import (
    dias_mora_temprana,
    siguiente_dia_habil,
    vencimiento_efectivo,
)


def test_sabado_30_mueve_vencimiento_a_lunes():
    # Marzo 2026: día 30 es lunes; usamos un mes donde 30 cae sábado (abril 2026 no)
    # Junio 2026: día 30 es martes. Mayo 2026: 30 es sábado.
    feriados: set[date] = set()
    venc = vencimiento_efectivo(2026, 5, 30, feriados)
    assert venc.weekday() == 0  # lunes 1-jun-2026 (30-may-2026 es sábado)


def test_mora_un_dia_despues_del_vencimiento_habil():
    feriados: set[date] = set()
    venc = vencimiento_efectivo(2026, 5, 30, feriados)
    assert dias_mora_temprana(venc, 30, feriados) == 0
    from datetime import timedelta

    martes = venc + timedelta(days=1)
    assert dias_mora_temprana(martes, 30, feriados) == 1


def test_feriado_mueve_vencimiento():
    feriados = {date(2026, 6, 1)}
    nominal = date(2026, 6, 1)
    assert siguiente_dia_habil(nominal, feriados) == date(2026, 6, 2)
