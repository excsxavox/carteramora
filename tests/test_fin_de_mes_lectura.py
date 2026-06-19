from datetime import date

from cobranzas.application.chain.lectura_cartera_handler import LecturaCarteraHandler
from cobranzas.application.chain.lectura_morosidad_handler import (
    LecturaMorosidadHandler,
)
from cobranzas.application.chain.proceso_context import ProcesoContext
from cobranzas.domain.models.credito import Credito
from cobranzas.domain.services.cartera_merge_service import CarteraMergeService


class _RepoFalla:
    def obtener_creditos(self):
        raise AssertionError("No se debe leer CAMOROSICO en fin de mes")


class _RepoCartera:
    def __init__(self, creditos):
        self._creditos = creditos

    def obtener_creditos(self):
        return self._creditos


def _credito(op: str, dias: int) -> Credito:
    return Credito(op, "CLIENTE", 100.0, dias, date(2026, 6, 30), estado_operacion="VIGENTE")


def test_fin_de_mes_no_lee_camorosico():
    handler = LecturaMorosidadHandler(_RepoFalla())
    ctx = ProcesoContext(dias_mora_minimo=1, es_fin_de_mes=True)

    resultado = handler._procesar(ctx)

    assert resultado.creditos == []
    assert resultado.creditos_morosidad == []
    assert resultado.columnas_morosidad == ()


def test_fin_de_mes_usa_cadetacaco_como_base_sin_merge():
    cartera = [_credito("001", 5), _credito("002", 40)]
    handler = LecturaCarteraHandler(_RepoCartera(cartera), CarteraMergeService())
    ctx = ProcesoContext(dias_mora_minimo=1, es_fin_de_mes=True)
    ctx.creditos = []  # camorosico omitido

    resultado = handler._procesar(ctx)

    assert resultado.creditos == cartera
    assert resultado.total_cartera_leidas == 2
    assert resultado.total_enriquecidos == 2


def test_pipeline_normal_si_lee_camorosico():
    morosidad = [_credito("001", 5)]
    handler = LecturaMorosidadHandler(_RepoCartera(morosidad))
    ctx = ProcesoContext(dias_mora_minimo=1, es_fin_de_mes=False)

    resultado = handler._procesar(ctx)

    assert len(resultado.creditos) == 1
    assert resultado.creditos_morosidad == morosidad
