from datetime import date
from pathlib import Path

import pytest

from cobranzas.application.use_cases.procesar_cobranzas import (
    ProcesarCobranzasUseCase,
)
from cobranzas.domain.models.credito import EstadoMora
from cobranzas.domain.services.cobranzas_service import CobranzasService
from cobranzas.domain.services.cartera_merge_service import CarteraMergeService
from cobranzas.infrastructure.adapters.cuadro_morosidad_parser import (
    leer_cuadro_morosidad,
)
from cobranzas.infrastructure.adapters.tsv_credito_repository import (
    TsvCreditoRepository,
)
from cobranzas.infrastructure.adapters.tsv_cartera_repository import (
    TsvCarteraRepository,
)
from cobranzas.infrastructure.adapters.tsv_file_io import leer_creditos_tsv
from cobranzas.infrastructure.config.settings import Settings

FIXTURE_MOROSIDAD = (
    Path(__file__).parent / "fixtures" / "cuadro_morosidad_consolidado.txt"
)
FIXTURE_CARTERA = Path(__file__).parent / "fixtures" / "te_detallado_cartera.txt"

OPERACIONES_ESPERADAS = {
    "0015219214": {
        "cliente": "MINGA SALINAS MANUEL FRANCISCO",
        "dias_atraso": 136,
        "saldo_atrasado": 611.30,
        "estado": "RESOLUCION",
        "socio": "83736",
    },
    "0016280143": {
        "cliente": "NOVOA SANCHEZ LIGIA PIEDAD",
        "dias_atraso": 24,
        "saldo_atrasado": 53.94,
        "estado": "VIGENTE",
        "socio": "37245",
    },
    "0015389875": {
        "cliente": "ESCOBAR QUINATOA MARTHA CECILIA",
        "dias_atraso": 303,
        "saldo_atrasado": 1639.78,
        "estado": "VENCIDO",
        "socio": "250799",
    },
}


@pytest.fixture
def fecha_corte_y_creditos():
    return leer_cuadro_morosidad(FIXTURE_MOROSIDAD)


def test_parse_fecha_corte_desde_encabezado(fecha_corte_y_creditos):
    fecha_corte, _, _ = fecha_corte_y_creditos
    assert fecha_corte == date(2026, 3, 6)


def test_parse_nueve_operaciones_del_cuadro(fecha_corte_y_creditos):
    _, _, creditos = fecha_corte_y_creditos
    assert len(creditos) == 9
    numeros = {c.id_credito for c in creditos}
    assert set(OPERACIONES_ESPERADAS.keys()).issubset(numeros)


@pytest.mark.parametrize(
    "no_operacion,esperado",
    [
        ("0015219214", OPERACIONES_ESPERADAS["0015219214"]),
        ("0016280143", OPERACIONES_ESPERADAS["0016280143"]),
        ("0015389875", OPERACIONES_ESPERADAS["0015389875"]),
    ],
)
def test_mapeo_campos_operacion(fecha_corte_y_creditos, no_operacion, esperado):
    _, _, creditos = fecha_corte_y_creditos
    op = next(c for c in creditos if c.id_credito == no_operacion)

    assert op.cliente == esperado["cliente"]
    assert op.dias_mora == esperado["dias_atraso"]
    assert op.saldo_pendiente == pytest.approx(esperado["saldo_atrasado"])
    assert op.estado_operacion == esperado["estado"]
    assert op.socio == esperado["socio"]
    assert op.oficina == "CAYAMBE"


def test_minga_salinAS_clasificacion_mora_grave(fecha_corte_y_creditos):
    _, _, creditos = fecha_corte_y_creditos
    op = next(c for c in creditos if c.id_credito == "0015219214")
    assert op.clasificar_mora(30) == EstadoMora.MORA_GRAVE


def test_novoa_24_dias_no_esta_en_mora_con_umbral_30(fecha_corte_y_creditos):
    _, _, creditos = fecha_corte_y_creditos
    op = next(c for c in creditos if c.id_credito == "0016280143")
    assert op.esta_en_mora(30) is False


def test_filtrado_siete_operaciones_en_mora_umbral_30(fecha_corte_y_creditos):
    _, _, creditos = fecha_corte_y_creditos
    en_mora = CobranzasService().filtrar_en_mora(creditos, dias_mora_minimo=30)
    assert len(en_mora) == 7


def test_total_saldo_capital_atrasado_en_mora(fecha_corte_y_creditos):
    _, _, creditos = fecha_corte_y_creditos
    en_mora = CobranzasService().filtrar_en_mora(creditos, dias_mora_minimo=30)
    total = sum(c.saldo_pendiente for c in en_mora)
    assert total == pytest.approx(6224.29)


def test_leer_creditos_tsv_detecta_cuadro():
    creditos = leer_creditos_tsv(FIXTURE_MOROSIDAD)
    assert len(creditos) == 9


def test_job_completo_dos_archivos(tmp_path: Path):
    use_case = ProcesarCobranzasUseCase.crear(
        morosidad_repository=TsvCreditoRepository(FIXTURE_MOROSIDAD),
        cartera_repository=TsvCarteraRepository(FIXTURE_CARTERA),
        cobranzas_service=CobranzasService(),
        cartera_merge_service=CarteraMergeService(),
        dias_mora_minimo=30,
        archivo_morosidad=FIXTURE_MOROSIDAD,
        archivo_cartera=FIXTURE_CARTERA,
        archivo_detalle_morosidad=tmp_path / "detalle_morosidad.lis",
        archivo_detalle_mora=tmp_path / "reporte_mora.lis",
    )
    result = use_case.ejecutar()

    assert result.total_creditos_procesados == 9
    assert result.total_en_mora == 7
    assert result.total_saldo_mora == pytest.approx(6224.29)
    assert (tmp_path / "detalle_morosidad.lis").exists()
    assert (tmp_path / "reporte_mora.lis").exists()
    assert not (tmp_path / "reporte_mora.json").exists()
    assert not (tmp_path / "manifiesto.lis").exists()


def test_job_con_settings(tmp_path: Path):
    settings = Settings(
        ARCHIVO_MOROSIDAD=str(FIXTURE_MOROSIDAD),
        ARCHIVO_CARTERA=str(FIXTURE_CARTERA),
        ARCHIVO_SALIDA_MOROSIDAD=str(tmp_path / "detalle_morosidad.lis"),
        ARCHIVO_SALIDA_MORA=str(tmp_path / "reporte_mora.lis"),
        DIAS_MORA_MINIMO=30,
        PERSISTIR_EN_BD=False,
    )
    use_case = ProcesarCobranzasUseCase.crear(
        morosidad_repository=TsvCreditoRepository(settings.archivo_morosidad),
        cartera_repository=TsvCarteraRepository(settings.archivo_cartera),
        cobranzas_service=CobranzasService(),
        cartera_merge_service=CarteraMergeService(),
        dias_mora_minimo=settings.dias_mora_minimo,
        archivo_morosidad=settings.archivo_morosidad,
        archivo_cartera=settings.archivo_cartera,
        archivo_detalle_morosidad=settings.archivo_salida_morosidad,
        archivo_detalle_mora=settings.archivo_salida_mora,
    )
    result = use_case.ejecutar()
    assert result.total_en_mora == 7
    assert settings.archivo_salida_morosidad.exists()
    assert settings.archivo_salida_mora.exists()
