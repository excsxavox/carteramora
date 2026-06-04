from datetime import date
from pathlib import Path

import pytest

from cartera_mora.application.use_cases.procesar_cartera_mora import (
    ProcesarCarteraMoraUseCase,
)
from cartera_mora.domain.models.credito import EstadoMora
from cartera_mora.domain.services.cartera_mora_service import CarteraMoraService
from cartera_mora.domain.services.cartera_merge_service import CarteraMergeService
from cartera_mora.infrastructure.adapters.cuadro_morosidad_parser import (
    leer_cuadro_morosidad,
)
from cartera_mora.infrastructure.adapters.json_reporte_repository import (
    JsonReporteRepository,
)
from cartera_mora.infrastructure.adapters.tsv_credito_repository import (
    TsvCreditoRepository,
)
from cartera_mora.infrastructure.adapters.tsv_cartera_repository import (
    TsvCarteraRepository,
)
from cartera_mora.infrastructure.adapters.tsv_file_io import leer_creditos_tsv
from cartera_mora.infrastructure.adapters.lis_manifiesto_repository import (
    LisManifiestoRepository,
)
from cartera_mora.infrastructure.config.settings import Settings
from cartera_mora.domain.services.manifiesto_lis_service import ManifiestoLisService
from tests.test_chain import FakeManifiestoRepo, FakeReporteRepo

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
    fecha_corte, _ = fecha_corte_y_creditos
    assert fecha_corte == date(2026, 3, 6)


def test_parse_nueve_operaciones_del_cuadro(fecha_corte_y_creditos):
    _, creditos = fecha_corte_y_creditos
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
    _, creditos = fecha_corte_y_creditos
    op = next(c for c in creditos if c.id_credito == no_operacion)

    assert op.cliente == esperado["cliente"]
    assert op.dias_mora == esperado["dias_atraso"]
    assert op.saldo_pendiente == pytest.approx(esperado["saldo_atrasado"])
    assert op.estado_operacion == esperado["estado"]
    assert op.socio == esperado["socio"]
    assert op.oficina == "CAYAMBE"


def test_minga_salinAS_clasificacion_mora_grave(fecha_corte_y_creditos):
    _, creditos = fecha_corte_y_creditos
    op = next(c for c in creditos if c.id_credito == "0015219214")
    assert op.clasificar_mora(30) == EstadoMora.MORA_GRAVE


def test_novoa_24_dias_no_esta_en_mora_con_umbral_30(fecha_corte_y_creditos):
    _, creditos = fecha_corte_y_creditos
    op = next(c for c in creditos if c.id_credito == "0016280143")
    assert op.esta_en_mora(30) is False


def test_filtrado_siete_operaciones_en_mora_umbral_30(fecha_corte_y_creditos):
    _, creditos = fecha_corte_y_creditos
    en_mora = CarteraMoraService().filtrar_en_mora(creditos, dias_mora_minimo=30)
    assert len(en_mora) == 7


def test_total_saldo_capital_atrasado_en_mora(fecha_corte_y_creditos):
    _, creditos = fecha_corte_y_creditos
    en_mora = CarteraMoraService().filtrar_en_mora(creditos, dias_mora_minimo=30)
    total = sum(c.saldo_pendiente for c in en_mora)
    assert total == pytest.approx(6224.29)


def test_leer_creditos_tsv_detecta_cuadro():
    creditos = leer_creditos_tsv(FIXTURE_MOROSIDAD)
    assert len(creditos) == 9


def test_job_completo_dos_archivos(tmp_path: Path):
    use_case = ProcesarCarteraMoraUseCase.crear(
        morosidad_repository=TsvCreditoRepository(FIXTURE_MOROSIDAD),
        cartera_repository=TsvCarteraRepository(FIXTURE_CARTERA),
        reporte_repository=JsonReporteRepository(tmp_path / "reporte.json"),
        manifiesto_repository=LisManifiestoRepository(tmp_path / "reporte.lis"),
        cartera_mora_service=CarteraMoraService(),
        cartera_merge_service=CarteraMergeService(),
        manifiesto_lis_service=ManifiestoLisService(),
        dias_mora_minimo=30,
        archivo_morosidad=FIXTURE_MOROSIDAD,
        archivo_cartera=FIXTURE_CARTERA,
        archivo_reporte=tmp_path / "reporte.json",
        archivo_lis=tmp_path / "reporte.lis",
    )
    result = use_case.ejecutar()

    assert result.total_creditos_procesados == 9
    assert result.total_en_mora == 7
    assert result.total_saldo_mora == pytest.approx(6224.29)
    assert (tmp_path / "reporte.lis").exists()


def test_cadena_con_fixture_cuadro(tmp_path: Path):
    reporte_repo = FakeReporteRepo()
    manifiesto_repo = FakeManifiestoRepo()
    use_case = ProcesarCarteraMoraUseCase.crear(
        morosidad_repository=TsvCreditoRepository(FIXTURE_MOROSIDAD),
        cartera_repository=TsvCarteraRepository(FIXTURE_CARTERA),
        reporte_repository=reporte_repo,
        manifiesto_repository=manifiesto_repo,
        cartera_mora_service=CarteraMoraService(),
        cartera_merge_service=CarteraMergeService(),
        manifiesto_lis_service=ManifiestoLisService(),
        dias_mora_minimo=30,
        archivo_morosidad=FIXTURE_MOROSIDAD,
        archivo_cartera=FIXTURE_CARTERA,
        archivo_reporte=tmp_path / "r.json",
        archivo_lis=tmp_path / "r.lis",
    )
    result = use_case.ejecutar()

    assert result.total_en_mora == 7
    assert reporte_repo.guardado is not None
    assert reporte_repo.guardado["fecha_corte"] == "2026-03-06"


def test_job_con_settings(tmp_path: Path):
    settings = Settings(
        ARCHIVO_MOROSIDAD=str(FIXTURE_MOROSIDAD),
        ARCHIVO_CARTERA=str(FIXTURE_CARTERA),
        ARCHIVO_SALIDA=str(tmp_path / "reporte.json"),
        ARCHIVO_LIS=str(tmp_path / "reporte.lis"),
        DIAS_MORA_MINIMO=30,
    )
    use_case = ProcesarCarteraMoraUseCase.crear(
        morosidad_repository=TsvCreditoRepository(settings.archivo_morosidad),
        cartera_repository=TsvCarteraRepository(settings.archivo_cartera),
        reporte_repository=JsonReporteRepository(settings.archivo_salida),
        manifiesto_repository=LisManifiestoRepository(settings.archivo_lis),
        cartera_mora_service=CarteraMoraService(),
        cartera_merge_service=CarteraMergeService(),
        manifiesto_lis_service=ManifiestoLisService(),
        dias_mora_minimo=settings.dias_mora_minimo,
        archivo_morosidad=settings.archivo_morosidad,
        archivo_cartera=settings.archivo_cartera,
        archivo_reporte=settings.archivo_salida,
        archivo_lis=settings.archivo_lis,
    )
    result = use_case.ejecutar()
    assert result.total_en_mora == 7
    assert settings.archivo_salida.exists()
    assert settings.archivo_lis.exists()
