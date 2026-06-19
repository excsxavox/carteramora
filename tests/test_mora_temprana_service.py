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
        dias_mora=12,
        fecha_corte=date(2026, 6, 2),
        estado_operacion="VIGENTE",
        tipo_operacion="CONSUMO23",
        campos_tab=(
            ("dia_pago", "15"),
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


def test_lista_blanca_permite_vigente_y_resolucion():
    permitidos = ("RESOLUCION", "VIGENTE")
    vigente = _credito(estado_operacion="VIGENTE")
    resolucion = _credito(estado_operacion="RESOLUCION")
    excl_v, _ = debe_excluir_operacion(vigente, (), (), permitidos)
    excl_r, _ = debe_excluir_operacion(resolucion, (), (), permitidos)
    assert not excl_v
    assert not excl_r


def test_lista_blanca_excluye_vencido():
    excluir, motivo = debe_excluir_operacion(
        _credito(estado_operacion="VENCIDO"), (), (), ("RESOLUCION", "VIGENTE")
    )
    assert excluir
    assert "estado_no_permitido" in motivo


def test_procesar_filtra_por_lista_blanca_de_estados():
    servicio = MoraTempranaService()
    creditos = [
        _credito(id_credito="V", estado_operacion="VIGENTE", dias_mora=10),
        _credito(id_credito="R", estado_operacion="RESOLUCION", dias_mora=10),
        _credito(id_credito="X", estado_operacion="VENCIDO", dias_mora=10),
    ]
    elegibles, metricas = servicio.procesar(
        creditos,
        feriados=set(),
        estados_permitidos=("RESOLUCION", "VIGENTE"),
    )
    ids = {c.id_credito for c in elegibles}
    assert ids == {"V", "R"}
    assert metricas["excluidos_regla"] == 1


def test_temprana_antes_de_limite_mes_siguiente():
    """dia_pago 15, corte 02-jun, cuota mayo vencida (15-may); límite 15-jun."""
    servicio = MoraTempranaService()
    credito = _credito(
        id_credito="TEMPRANA",
        fecha_corte=date(2026, 6, 2),
        dias_mora=12,
        campos_tab=(("dia_pago", "15"), ("cuotas_atr", "1")),
    )
    elegibles, metricas = servicio.procesar(
        [credito],
        feriados=set(),
        estados_excluidos=(),
        tipos_oper_excluidos=(),
    )
    assert len(elegibles) == 1
    assert metricas["en_mora_temprana"] == 1


def test_dias_mora_se_conserva_de_camorosico():
    """El valor de días no se recalcula: queda el de CAMOROSICO."""
    servicio = MoraTempranaService()
    credito = _credito(
        id_credito="DIAS",
        fecha_corte=date(2026, 5, 20),
        dias_mora=10,
        campos_tab=(("dia_pago", "5"), ("cuotas_atr", "1")),
    )
    elegibles, _ = servicio.procesar(
        [credito],
        feriados=set(),
        estados_excluidos=(),
        tipos_oper_excluidos=(),
    )
    assert len(elegibles) == 1
    assert elegibles[0].dias_mora == 10


def test_supera_tope_29_dias_es_madura():
    """Más de 29 días de mora → fuera del rango de mora temprana (no elegible)."""
    servicio = MoraTempranaService()
    credito = _credito(
        id_credito="SUPERA",
        fecha_corte=date(2026, 6, 20),
        dias_mora=36,
        campos_tab=(("dia_pago", "15"), ("cuotas_atr", "1")),
    )
    elegibles, metricas = servicio.procesar(
        [credito],
        feriados=set(),
        estados_excluidos=(),
        tipos_oper_excluidos=(),
    )
    assert len(elegibles) == 0
    assert metricas["fuera_rango_dias"] == 1
    assert metricas["dias_max"] == 29


def test_fin_de_mes_sin_tope_incluye_mora_madura():
    """Con es_fin_de_mes=True no hay tope: 301 días sigue siendo elegible."""
    servicio = MoraTempranaService()
    credito = _credito(
        id_credito="FINMES",
        fecha_corte=date(2026, 6, 30),
        dias_mora=301,
        campos_tab=(("dia_pago", "15"), ("cuotas_atr", "5")),
    )
    elegibles, metricas = servicio.procesar(
        [credito],
        feriados=set(),
        estados_excluidos=(),
        tipos_oper_excluidos=(),
        es_fin_de_mes=True,
    )
    assert len(elegibles) == 1
    assert metricas["fuera_rango_dias"] == 0
    assert metricas["es_fin_de_mes"] is True


def test_fin_de_mes_sigue_aplicando_piso():
    """Aun en fin de mes, días < piso (0 días) no entran."""
    servicio = MoraTempranaService()
    credito = _credito(id_credito="ALDIA", dias_mora=0)
    elegibles, _ = servicio.procesar(
        [credito],
        feriados=set(),
        estados_excluidos=(),
        tipos_oper_excluidos=(),
        es_fin_de_mes=True,
    )
    assert len(elegibles) == 0


def test_exactamente_29_dias_es_temprana():
    """29 días de mora está dentro del rango [1-29] → elegible."""
    servicio = MoraTempranaService()
    credito = _credito(
        id_credito="LIMITE29",
        fecha_corte=date(2026, 6, 2),
        dias_mora=29,
        campos_tab=(("dia_pago", "15"), ("cuotas_atr", "1")),
    )
    elegibles, metricas = servicio.procesar(
        [credito],
        feriados=set(),
        estados_excluidos=(),
        tipos_oper_excluidos=(),
    )
    assert len(elegibles) == 1
    assert metricas["en_mora_temprana"] == 1


def test_treinta_dias_fuera_de_rango():
    """30 días supera el tope de 29 → no elegible."""
    servicio = MoraTempranaService()
    credito = _credito(
        id_credito="TREINTA",
        fecha_corte=date(2026, 6, 2),
        dias_mora=30,
        campos_tab=(("dia_pago", "15"), ("cuotas_atr", "1")),
    )
    elegibles, metricas = servicio.procesar(
        [credito],
        feriados=set(),
        estados_excluidos=(),
        tipos_oper_excluidos=(),
    )
    assert len(elegibles) == 0
    assert metricas["fuera_rango_dias"] == 1


def test_tope_dias_configurable_via_dias_max():
    """El tope es configurable: con dias_max=60, 36 días entra como temprana."""
    servicio = MoraTempranaService()
    credito = _credito(
        id_credito="CONFIG",
        fecha_corte=date(2026, 6, 20),
        dias_mora=36,
        campos_tab=(("dia_pago", "15"), ("cuotas_atr", "1")),
    )
    elegibles, metricas = servicio.procesar(
        [credito],
        feriados=set(),
        dias_max=60,
        estados_excluidos=(),
        tipos_oper_excluidos=(),
    )
    assert len(elegibles) == 1
    assert metricas["dias_max"] == 60


def test_sin_dias_atraso_no_entra():
    servicio = MoraTempranaService()
    credito = _credito(dias_mora=0)
    elegibles, metricas = servicio.procesar(
        [credito],
        feriados=set(),
        estados_excluidos=(),
        tipos_oper_excluidos=(),
    )
    assert len(elegibles) == 0
    assert metricas["sin_dias_atraso"] == 1


def test_sin_dia_pago_igual_entra_solo_importan_los_dias():
    """La elegibilidad depende solo de los días de CAMOROSICO; el día de pago
    ya no condiciona."""
    servicio = MoraTempranaService()
    credito = _credito(dias_mora=5, campos_tab=())
    elegibles, metricas = servicio.procesar(
        [credito],
        feriados=set(),
        estados_excluidos=(),
        tipos_oper_excluidos=(),
    )
    assert len(elegibles) == 1
    assert metricas["en_mora_temprana"] == 1


def test_ordena_por_saldo_capital_descendente():
    servicio = MoraTempranaService()
    creditos = [
        _credito(
            id_credito="CHICO",
            campos_tab=(("dia_pago", "15"), ("saldo_cap_prest", "1000")),
        ),
        _credito(
            id_credito="GRANDE",
            campos_tab=(("dia_pago", "15"), ("saldo_cap_prest", "9000")),
        ),
    ]
    elegibles, _ = servicio.procesar(
        [creditos[0], creditos[1]],
        feriados=set(),
        estados_excluidos=(),
        tipos_oper_excluidos=(),
    )
    assert [c.id_credito for c in elegibles] == ["GRANDE", "CHICO"]
