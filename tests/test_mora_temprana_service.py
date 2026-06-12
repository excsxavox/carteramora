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
        campos_tab=(
            ("dia_pago", "1"),
            ("saldo_cap_prest", "5000"),
            ("cuotas_atr", "1"),
        ),
    )
    base.update(kwargs)
    return Credito(**base)


def test_excluye_castigado():
    c = _credito(estado_operacion="CASTIGADO")
    excluir, _ = debe_excluir_operacion(c, ("CASTIGADO",), ())
    assert excluir


def test_filtra_por_dias_habiles_dia_pago():
    servicio = MoraTempranaService()
    creditos = [
        _credito(
            id_credito="A",
            fecha_corte=date(2026, 6, 1),
            dias_mora=99,
            campos_tab=(("dia_pago", "1"), ("cuotas_atr", "2")),
        ),
        _credito(
            id_credito="B",
            fecha_corte=date(2026, 6, 1),
            dias_mora=1,
            campos_tab=(
                ("dia_pago", "1"),
                ("cuotas_atr", "1"),
                ("fecha_ultimo_pago", "06/01/2026"),
            ),
        ),
    ]
    elegibles, _ = servicio.procesar(
        creditos,
        feriados=set(),
        dias_min=1,
        dias_max=1,
        estados_excluidos=(),
        tipos_oper_excluidos=(),
    )
    assert len(elegibles) == 1
    assert elegibles[0].id_credito == "B"
    assert elegibles[0].dias_mora == 1


def test_sin_ultimo_pago_puede_entrar_temprana():
    servicio = MoraTempranaService()
    credito = _credito(
        id_credito="SIN_PAGO",
        fecha_corte=date(2026, 5, 5),
        dias_mora=1,
        campos_tab=(("dia_pago", "5"), ("cuotas_atr", "1")),
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


def test_camorosico_3_con_un_dia_habil_entra():
    servicio = MoraTempranaService()
    credito = _credito(
        id_credito="CALENDARIO",
        fecha_corte=date(2026, 5, 5),
        dias_mora=3,
        campos_tab=(
            ("dia_pago", "5"),
            ("cuotas_atr", "1"),
            ("fecha_ultimo_pago", "04/06/2026"),
        ),
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


def test_ref_camorosico_alto_mismo_mes_sigue_temprana_con_max_calculado():
    """CAMOROSICO en calendario no cambia mora temprana si la cuota es del mes de corte."""
    servicio = MoraTempranaService()
    credito = _credito(
        id_credito="0018521943",
        fecha_corte=date(2026, 5, 20),
        dias_mora=34,
        campos_tab=(("dia_pago", "5"), ("cuotas_atr", "1")),
    )
    elegibles, _ = servicio.procesar(
        [credito],
        feriados=set(),
        dias_min=1,
        dias_max=0,
        estados_excluidos=(),
        tipos_oper_excluidos=(),
    )
    assert len(elegibles) == 1
    assert elegibles[0].dias_mora > 1


def test_junio_5_dia_pago_2_ref_camorosico_6_entra_temprana():
    servicio = MoraTempranaService()
    credito = _credito(
        id_credito="0018218948",
        fecha_corte=date(2026, 6, 5),
        dias_mora=6,
        campos_tab=(("dia_pago", "2"), ("cuotas_atr", "1")),
    )
    elegibles, _ = servicio.procesar(
        [credito],
        feriados=set(),
        dias_min=1,
        dias_max=0,
        estados_excluidos=(),
        tipos_oper_excluidos=(),
    )
    assert len(elegibles) == 1
    assert elegibles[0].dias_mora == 4


def test_archivo_viernes_dia_pago_consulta_lunes_entra_temprana():
    """0130089154: archivo 5-jun (vie), consulta 8-jun, 1 día hábil mora."""
    servicio = MoraTempranaService()
    credito = _credito(
        id_credito="0130089154",
        fecha_corte=date(2026, 6, 5),
        dias_mora=3,
        campos_tab=(
            ("dia_pago", "5"),
            ("cuotas_atr", "1"),
            ("fecha_ultimo_pago", "05/05/2026"),
        ),
    )
    elegibles, _ = servicio.procesar(
        [credito],
        feriados=set(),
        dias_min=1,
        dias_max=0,
        estados_excluidos=(),
        tipos_oper_excluidos=(),
    )
    assert len(elegibles) == 1
    assert elegibles[0].dias_mora == 1


def test_varios_dias_dentro_plazo_cuota_entra_temprana():
    servicio = MoraTempranaService()
    credito = _credito(
        id_credito="PLAZO",
        fecha_corte=date(2026, 5, 20),
        dias_mora=10,
        campos_tab=(("dia_pago", "5"), ("cuotas_atr", "1")),
    )
    elegibles, _ = servicio.procesar(
        [credito],
        feriados=set(),
        dias_min=1,
        dias_max=0,
        estados_excluidos=(),
        tipos_oper_excluidos=(),
    )
    assert len(elegibles) == 1
    assert elegibles[0].dias_mora > 1


def test_mayo_impago_junio_1_una_cuota_vencida_es_madura_por_cruce_mes():
    servicio = MoraTempranaService()
    credito = _credito(
        id_credito="MAY_IMPAGA",
        fecha_corte=date(2026, 6, 1),
        dias_mora=17,
        campos_tab=(
            ("dia_pago", "15"),
            ("cuotas_atr", "1"),
            ("fecha_ultimo_pago", "04/21/2026"),
        ),
    )
    elegibles, metricas = servicio.procesar(
        [credito],
        feriados=set(),
        dias_min=1,
        dias_max=0,
        estados_excluidos=(),
        tipos_oper_excluidos=(),
    )
    assert len(elegibles) == 0
    assert metricas["mora_madura_cruce_mes"] == 1


def test_cuotas_atr_distinto_de_un_no_entra_temprana():
    servicio = MoraTempranaService()
    credito = _credito(
        id_credito="CUOTAS2",
        fecha_corte=date(2026, 6, 11),
        dias_mora=15,
        campos_tab=(
            ("dia_pago", "10"),
            ("cuotas_atr", "2"),
            ("fecha_ultimo_pago", "05/12/2026"),
        ),
    )
    elegibles, metricas = servicio.procesar(
        [credito],
        feriados=set(),
        dias_min=1,
        dias_max=0,
        estados_excluidos=(),
        tipos_oper_excluidos=(),
    )
    assert len(elegibles) == 0
    assert metricas["cuotas_atr_no_temprana"] == 1


def test_sin_dia_pago_no_entra():
    servicio = MoraTempranaService()
    credito = _credito(dias_mora=1, campos_tab=())
    elegibles, metricas = servicio.procesar(
        [credito],
        feriados=set(),
        dias_min=1,
        dias_max=1,
        estados_excluidos=(),
        tipos_oper_excluidos=(),
    )
    assert len(elegibles) == 0
    assert metricas["sin_dia_pago"] == 1
