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
        campos_tab=(("dia_pago", "1"), ("saldo_cap_prest", "5000")),
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
        _credito(id_credito="A", dias_mora=99, campos_tab=(("dia_pago", "1"),)),
        _credito(
            id_credito="B",
            dias_mora=1,
            campos_tab=(
                ("dia_pago", "1"),
                ("fecha_ultimo_pago", "01/06/2026"),
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
        fecha_corte=date(2026, 5, 6),
        dias_mora=1,
        campos_tab=(("dia_pago", "5"),),
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
        fecha_corte=date(2026, 5, 6),
        dias_mora=3,
        campos_tab=(("dia_pago", "5"), ("fecha_ultimo_pago", "05/05/2026")),
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


def test_34_dias_camorosico_no_entra_mora_temprana():
    servicio = MoraTempranaService()
    credito = _credito(
        id_credito="0018521943",
        fecha_corte=date(2026, 5, 6),
        dias_mora=34,
        campos_tab=(
            ("dia_pago", "5"),
            ("fecha_ultimo_pago", "06/01/2026"),
        ),
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
    assert (
        metricas["mora_madura_periodos_anteriores"] == 1
        or metricas["mora_madura_acumulada"] == 1
    )


def test_varios_dias_dentro_plazo_cuota_entra_temprana():
    servicio = MoraTempranaService()
    credito = _credito(
        id_credito="PLAZO",
        fecha_corte=date(2026, 5, 20),
        dias_mora=10,
        campos_tab=(("dia_pago", "5"),),
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
