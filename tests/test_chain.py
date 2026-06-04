from datetime import date
from pathlib import Path
from typing import List

from cobranzas.application.chain.chain_builder import build_proceso_chain
from cobranzas.application.chain.proceso_context import ProcesoContext
from cobranzas.application.use_cases.procesar_cobranzas import (
    ProcesarCobranzasUseCase,
)
from cobranzas.domain.models.credito import Credito
from cobranzas.domain.ports.cartera_repository import CarteraRepositoryPort
from cobranzas.domain.ports.credito_repository import CreditoRepositoryPort
from cobranzas.domain.services.cobranzas_service import CobranzasService
from cobranzas.domain.services.cartera_merge_service import CarteraMergeService


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


def test_cadena_genera_dos_archivos_lis(tmp_path: Path):
    chain = build_proceso_chain(
        morosidad_repository=FakeMorosidadRepo(),
        cartera_repository=FakeCarteraRepo(),
        cobranzas_service=CobranzasService(),
        cartera_merge_service=CarteraMergeService(),
    )
    morosidad_out = tmp_path / "detalle_morosidad.lis"
    mora_out = tmp_path / "detalle_mora.lis"
    contexto = ProcesoContext(
        dias_mora_minimo=30,
        archivo_morosidad=tmp_path / "mor.txt",
        archivo_cartera=tmp_path / "car.txt",
        archivo_detalle_morosidad=morosidad_out,
        archivo_detalle_mora=mora_out,
    )
    resultado = chain.manejar(contexto)

    assert resultado.reporte["total_creditos"] == 1
    assert morosidad_out.exists()
    assert mora_out.exists()
    assert len(resultado.creditos_mora) == 1


def test_use_case_con_cadena(tmp_path: Path):
    use_case = ProcesarCobranzasUseCase.crear(
        morosidad_repository=FakeMorosidadRepo(),
        cartera_repository=FakeCarteraRepo(),
        cobranzas_service=CobranzasService(),
        cartera_merge_service=CarteraMergeService(),
        dias_mora_minimo=30,
        archivo_morosidad=tmp_path / "m.txt",
        archivo_cartera=tmp_path / "c.txt",
        archivo_detalle_morosidad=tmp_path / "detalle_morosidad.lis",
        archivo_detalle_mora=tmp_path / "detalle_mora.lis",
    )
    result = use_case.ejecutar()

    assert result.total_en_mora == 1
    assert (tmp_path / "detalle_morosidad.lis").exists()
    assert (tmp_path / "detalle_mora.lis").exists()
