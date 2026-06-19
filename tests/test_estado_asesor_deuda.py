from datetime import date

from cobranzas.domain.models.credito import Credito
from cobranzas.infrastructure.persistence.mappers.cobranza_credito_mapper import (
    ESTADO_ASESOR_MORA_TEMPRANA,
    clasificacion_para_asignacion,
)


def test_estado_asignacion_mora_temprana_en_asesores_deuda():
    credito = Credito(
        "001",
        "CLIENTE",
        500.0,
        1,
        date(2026, 6, 4),
        estado_operacion="VIGENTE",
    )
    cat_valor, cat_desc, estado = clasificacion_para_asignacion(
        credito,
        dias_mora_minimo=30,
        usar_mora_temprana=True,
        mora_temprana_dias_min=1,
        mora_temprana_dias_max=1,
    )
    assert estado == ESTADO_ASESOR_MORA_TEMPRANA
    assert cat_valor == "mora_temprana"
    assert cat_desc == "Mora temprana"


def test_estado_asignacion_mora_temprana_con_max_calculado_cero():
    credito = Credito(
        "003",
        "CLIENTE",
        500.0,
        2,
        date(2026, 6, 3),
        estado_operacion="VIGENTE",
    )
    _, _, estado = clasificacion_para_asignacion(
        credito,
        dias_mora_minimo=30,
        usar_mora_temprana=True,
        mora_temprana_dias_min=1,
        mora_temprana_dias_max=0,
    )
    assert estado == ESTADO_ASESOR_MORA_TEMPRANA


def test_29_dias_es_mora_temprana_con_max_cero():
    credito = Credito(
        "004",
        "CLIENTE",
        500.0,
        29,
        date(2026, 6, 3),
        estado_operacion="VIGENTE",
    )
    _, _, estado = clasificacion_para_asignacion(
        credito,
        dias_mora_minimo=30,
        usar_mora_temprana=True,
        mora_temprana_dias_min=1,
        mora_temprana_dias_max=0,
    )
    assert estado == ESTADO_ASESOR_MORA_TEMPRANA


def test_30_dias_no_es_mora_temprana_con_max_cero():
    credito = Credito(
        "005",
        "CLIENTE",
        500.0,
        30,
        date(2026, 6, 3),
        estado_operacion="VIGENTE",
    )
    _, _, estado = clasificacion_para_asignacion(
        credito,
        dias_mora_minimo=30,
        usar_mora_temprana=True,
        mora_temprana_dias_min=1,
        mora_temprana_dias_max=0,
    )
    assert estado != ESTADO_ASESOR_MORA_TEMPRANA


def test_fin_de_mes_clasifica_mora_temprana_sin_tope():
    credito = Credito(
        "006",
        "CLIENTE",
        500.0,
        301,
        date(2026, 6, 30),
        estado_operacion="VIGENTE",
    )
    _, _, estado = clasificacion_para_asignacion(
        credito,
        dias_mora_minimo=30,
        usar_mora_temprana=True,
        mora_temprana_dias_min=1,
        mora_temprana_dias_max=0,
        es_fin_de_mes=True,
    )
    assert estado == ESTADO_ASESOR_MORA_TEMPRANA


def test_estado_operativo_queda_en_deuda_no_en_asignacion():
    credito = Credito(
        "002",
        "CLIENTE",
        500.0,
        45,
        date(2026, 6, 4),
        estado_operacion="VIGENTE",
    )
    _, _, estado_asignacion = clasificacion_para_asignacion(
        credito, dias_mora_minimo=30, usar_mora_temprana=False
    )
    assert estado_asignacion == "MORA_MADURA"
