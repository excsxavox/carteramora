from datetime import date

from cobranzas.domain.models.credito import Credito
from cobranzas.domain.services.mora_temprana_service import (
    MoraTempranaService,
    debe_excluir_operacion,
)


def _credito(**kwargs) -> Credito:
    base = dict(
        id_credito="001",
        cliente="CLIENTE",
        saldo_pendiente=100.0,
        dias_mora=5,
        fecha_corte=date(2026, 6, 2),
        estado_operacion="VIGENTE",
        tipo_operacion="CONSUMO23",
        campos_tab=(("dia_pago", "30"), ("saldo_cap_prest", "5000")),
    )
    base.update(kwargs)
    return Credito(**base)


def test_excluye_castigado():
    c = _credito(estado_operacion="CASTIGADO")
    excluir, _ = debe_excluir_operacion(c, ("CASTIGADO",), ())
    assert excluir


def test_filtra_por_dias_mora_temprana():
    servicio = MoraTempranaService()
    creditos = [
        _credito(id_credito="A", campos_tab=(("dia_pago", "1"),)),
        _credito(id_credito="B", campos_tab=(("dia_pago", "1"),)),
    ]
    elegibles, metricas = servicio.procesar(
        creditos,
        feriados=set(),
        dias_min=1,
        dias_max=29,
        estados_excluidos=(),
        tipos_oper_excluidos=(),
    )
    assert metricas["total_entrada"] == 2
    assert all(c.dias_mora >= 1 for c in elegibles)


def test_excluye_mora_madura_mes_anterior():
    servicio = MoraTempranaService()
    credito = _credito(
        id_credito="MADURA",
        fecha_corte=date(2026, 4, 6),
        campos_tab=(("dia_pago", "24"),),
    )
    elegibles, metricas = servicio.procesar(
        [credito],
        feriados=set(),
        dias_min=1,
        dias_max=29,
        estados_excluidos=(),
        tipos_oper_excluidos=(),
    )
    assert len(elegibles) == 0
    assert metricas["mora_madura_mes_anterior"] == 1


def test_sin_dia_pago_no_entra_en_temprana():
    servicio = MoraTempranaService()
    credito = _credito(
        id_credito="SIN_DP",
        dias_mora=10,
        campos_tab=(),
    )
    elegibles, metricas = servicio.procesar(
        [credito],
        feriados=set(),
        dias_min=1,
        dias_max=29,
        estados_excluidos=(),
        tipos_oper_excluidos=(),
    )
    assert len(elegibles) == 0
    assert metricas["sin_dia_pago_clasificar"] == 1
