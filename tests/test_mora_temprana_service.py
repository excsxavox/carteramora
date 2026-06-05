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


def test_excluye_por_est_cadetacaco_aunque_camorosico_vigente():
    c = _credito(
        estado_operacion="VIGENTE",
        campos_tab=(("est", "CASTIGADO"), ("dia_pago", "10")),
    )
    excluir, motivo = debe_excluir_operacion(c, ("CASTIGADO",), ())
    assert excluir
    assert "CASTIGADO" in motivo


def test_filtra_por_dias_desde_dia_pago():
    servicio = MoraTempranaService()
    creditos = [
        _credito(id_credito="A", dias_mora=99, campos_tab=(("dia_pago", "1"),)),
        _credito(
            id_credito="B",
            dias_mora=10,
            campos_tab=(("dia_pago", "2"),),
        ),
    ]
    elegibles, metricas = servicio.procesar(
        creditos,
        feriados=set(),
        dias_min=1,
        dias_max=1,
        estados_excluidos=(),
        tipos_oper_excluidos=(),
    )
    assert metricas["total_entrada"] == 2
    assert len(elegibles) == 1
    assert elegibles[0].dias_mora == 1


def test_excluye_si_dias_mayores_a_uno():
    servicio = MoraTempranaService()
    credito = _credito(
        id_credito="TEMPRANA",
        fecha_corte=date(2026, 4, 6),
        dias_mora=13,
        campos_tab=(("dia_pago", "24"),),
    )
    elegibles, _ = servicio.procesar(
        [credito],
        feriados=set(),
        dias_min=1,
        dias_max=1,
        estados_excluidos=(),
        tipos_oper_excluidos=(),
    )
    assert len(elegibles) == 0


def test_caso_27854_fuera_rango_con_4_dias():
    """ID Recblue 27854: 4 dias habiles -> no asigna (solo 1 dia)."""
    servicio = MoraTempranaService()
    credito = _credito(
        id_credito="0160005006",
        fecha_corte=date(2026, 4, 6),
        dias_mora=6,
        campos_tab=(("dia_pago", "30"),),
    )
    elegibles, metricas = servicio.procesar(
        [credito],
        feriados=set(),
        dias_min=1,
        dias_max=1,
        estados_excluidos=(),
        tipos_oper_excluidos=(),
    )
    assert len(elegibles) == 0
    assert metricas["fuera_rango_alto"] == 1


def test_solo_un_dia_habil_entra_temprana():
    servicio = MoraTempranaService()
    credito = _credito(
        id_credito="UN_DIA",
        fecha_corte=date(2026, 6, 2),
        campos_tab=(("dia_pago", "1"),),
    )
    elegibles, _ = servicio.procesar(
        [credito],
        feriados=set(),
        dias_min=1,
        dias_max=1,
        estados_excluidos=(),
        tipos_oper_excluidos=(),
    )
    assert len(elegibles) == 1
    assert elegibles[0].dias_mora == 1


def test_ultimo_pago_cubre_cuota_no_entra_temprana():
    servicio = MoraTempranaService()
    credito = _credito(
        id_credito="PAGADO",
        fecha_corte=date(2026, 4, 6),
        dias_mora=6,
        campos_tab=(
            ("dia_pago", "30"),
            ("fecha_ultimo_pago_ultimo_abono", "30/03/2026"),
        ),
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
    assert metricas["en_mora_temprana"] == 0


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
    assert metricas["sin_dia_pago"] == 1
