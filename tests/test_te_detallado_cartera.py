from datetime import date
from pathlib import Path

import pytest

from cartera_mora.domain.services.cartera_merge_service import CarteraMergeService
from cartera_mora.infrastructure.adapters.te_detallado_cartera_parser import (
    leer_te_detallado_cartera,
)

FIXTURE_CARTERA = Path(__file__).parent / "fixtures" / "te_detallado_cartera.txt"

OPERACIONES_CARTERA = {
    "0030070900": {
        "nombre": "VIZÑAY MAURIZACA ROSA ORTENCIA",
        "cedula": "0602411241",
        "dias_mora": 5392,
        "estado": "CASTIGADO",
        "calificacion": "E",
        "oficina": "TUMBACO",
    },
    "0015539937": {
        "nombre": "CHICAIZA VASQUEZ MARIA ESTHER",
        "cedula": "1711435410",
        "dias_mora": 0,
        "estado": "VIGENTE",
        "calificacion": "A1",
        "oficina": "CAYAMBE",
    },
    "0015568081": {
        "nombre": "CARRILLO ULCUANGO DAYSI LUCIA",
        "cedula": "1003174842",
        "dias_mora": 807,
        "estado": "JUDICIAL",
        "calificacion": "E",
        "oficina": "CAYAMBE",
    },
    "0015572965": {
        "nombre": "NOVOA SANCHEZ LIGIA PIEDAD",
        "cedula": "1701656736",
        "dias_mora": 0,
        "estado": "VIGENTE",
        "calificacion": "A1",
        "oficina": "CAYAMBE",
        "socio": "37245",
    },
}


@pytest.fixture
def fecha_corte_y_creditos_cartera():
    return leer_te_detallado_cartera(FIXTURE_CARTERA)


def test_parse_fecha_corte_cartera(fecha_corte_y_creditos_cartera):
    fecha_corte, _ = fecha_corte_y_creditos_cartera
    assert fecha_corte == date(2026, 3, 6)


def test_parse_operaciones_te_detallado(fecha_corte_y_creditos_cartera):
    _, creditos = fecha_corte_y_creditos_cartera
    assert len(creditos) == 14
    numeros = {c.id_credito for c in creditos}
    assert set(OPERACIONES_CARTERA.keys()).issubset(numeros)


@pytest.mark.parametrize(
    "numero_operacion,esperado",
    [(k, v) for k, v in OPERACIONES_CARTERA.items()],
)
def test_mapeo_campos_te_detallado(
    fecha_corte_y_creditos_cartera, numero_operacion, esperado
):
    _, creditos = fecha_corte_y_creditos_cartera
    op = next(c for c in creditos if c.id_credito == numero_operacion)

    assert op.cliente == esperado["nombre"]
    assert op.cedula == esperado["cedula"]
    assert op.dias_mora == esperado["dias_mora"]
    assert op.estado_operacion == esperado["estado"]
    assert op.calificacion == esperado["calificacion"]
    assert op.oficina == esperado["oficina"]
    if "socio" in esperado:
        assert op.socio == esperado["socio"]


def test_castigado_tumbaco_5392_dias_mora(fecha_corte_y_creditos_cartera):
    _, creditos = fecha_corte_y_creditos_cartera
    op = next(c for c in creditos if c.id_credito == "0030070900")
    assert op.estado_operacion == "CASTIGADO"
    assert op.dias_mora == 5392
    assert op.saldo_pendiente == pytest.approx(577.60)


def test_vigente_cayambe_al_dia(fecha_corte_y_creditos_cartera):
    _, creditos = fecha_corte_y_creditos_cartera
    op = next(c for c in creditos if c.id_credito == "0015539937")
    assert op.estado_operacion == "VIGENTE"
    assert op.dias_mora == 0
    assert op.esta_en_mora(30) is False


def test_merge_enriquece_morosidad_con_cedula():
    from cartera_mora.infrastructure.adapters.cuadro_morosidad_parser import (
        leer_cuadro_morosidad,
    )

    fixture_morosidad = (
        Path(__file__).parent / "fixtures" / "cuadro_morosidad_consolidado.txt"
    )
    _, morosidad = leer_cuadro_morosidad(fixture_morosidad)
    _, cartera = leer_te_detallado_cartera(FIXTURE_CARTERA)

    merge = CarteraMergeService()
    resultado = merge.enriquecer_con_cartera(morosidad, cartera)

    assert len(resultado) == len(morosidad)
    minga = next(c for c in resultado if c.id_credito == "0015219214")
    assert minga.dias_mora == 136
    assert minga.estado_operacion == "RESOLUCION"
