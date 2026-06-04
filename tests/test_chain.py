from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from cobranzas.application.chain.chain_builder import build_proceso_chain
from cobranzas.application.chain.proceso_context import ProcesoContext
from cobranzas.application.use_cases.procesar_cobranzas import (
    ProcesarCobranzasUseCase,
)
from cobranzas.domain.models.credito import Credito
from cobranzas.domain.ports.cartera_repository import CarteraRepositoryPort
from cobranzas.domain.ports.credito_repository import CreditoRepositoryPort
from cobranzas.domain.ports.manifiesto_repository import ManifiestoRepositoryPort
from cobranzas.domain.ports.reporte_repository import ReporteRepositoryPort
from cobranzas.domain.services.cobranzas_service import CobranzasService
from cobranzas.domain.services.cartera_merge_service import CarteraMergeService
from cobranzas.domain.services.manifiesto_lis_service import ManifiestoLisService


class FakeMorosidadRepo(CreditoRepositoryPort):
    def obtener_creditos(self) -> List[Credito]:
        return [
            Credito("1", "A", 100.0, 45, date(2026, 3, 6)),
            Credito("2", "B", 200.0, 10, date(2026, 3, 6)),
        ]


class FakeCarteraRepo(CarteraRepositoryPort):
    def obtener_creditos(self) -> List[Credito]:
        return [
            Credito(
                "1",
                "A",
                500.0,
                0,
                date(2026, 3, 6),
                cedula="123",
                calificacion="A1",
            ),
        ]


class FakeReporteRepo(ReporteRepositoryPort):
    def __init__(self) -> None:
        self.guardado: Optional[Dict[str, Any]] = None

    def guardar_reporte(self, reporte: Dict[str, Any]) -> None:
        self.guardado = reporte


class FakeManifiestoRepo(ManifiestoRepositoryPort):
    def __init__(self) -> None:
        self.contenido: Optional[str] = None

    def guardar_manifiesto(self, contenido: str) -> None:
        self.contenido = contenido


def test_cadena_genera_lis(tmp_path: Path):
    reporte_repo = FakeReporteRepo()
    manifiesto_repo = FakeManifiestoRepo()

    chain = build_proceso_chain(
        morosidad_repository=FakeMorosidadRepo(),
        cartera_repository=FakeCarteraRepo(),
        reporte_repository=reporte_repo,
        manifiesto_repository=manifiesto_repo,
        cobranzas_service=CobranzasService(),
        cartera_merge_service=CarteraMergeService(),
        manifiesto_lis_service=ManifiestoLisService(),
    )
    contexto = ProcesoContext(
        dias_mora_minimo=30,
        archivo_morosidad=tmp_path / "mor.txt",
        archivo_cartera=tmp_path / "car.txt",
        archivo_reporte=tmp_path / "out.json",
        archivo_lis=tmp_path / "out.lis",
    )
    resultado = chain.manejar(contexto)

    assert reporte_repo.guardado is not None
    assert manifiesto_repo.contenido is not None
    assert "ARCHIVOS LEIDOS" in manifiesto_repo.contenido
    assert "mor.txt" in manifiesto_repo.contenido
    assert len(resultado.creditos_mora) == 1


def test_use_case_con_cadena(tmp_path: Path):
    reporte_repo = FakeReporteRepo()
    manifiesto_repo = FakeManifiestoRepo()
    use_case = ProcesarCobranzasUseCase.crear(
        morosidad_repository=FakeMorosidadRepo(),
        cartera_repository=FakeCarteraRepo(),
        reporte_repository=reporte_repo,
        manifiesto_repository=manifiesto_repo,
        cobranzas_service=CobranzasService(),
        cartera_merge_service=CarteraMergeService(),
        manifiesto_lis_service=ManifiestoLisService(),
        dias_mora_minimo=30,
        archivo_morosidad=tmp_path / "m.txt",
        archivo_cartera=tmp_path / "c.txt",
        archivo_reporte=tmp_path / "r.json",
        archivo_lis=tmp_path / "r.lis",
    )
    result = use_case.ejecutar()

    assert result.total_en_mora == 1
    assert manifiesto_repo.contenido is not None
