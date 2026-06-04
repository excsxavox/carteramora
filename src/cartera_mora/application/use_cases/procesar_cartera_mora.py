from dataclasses import dataclass
from pathlib import Path

from cartera_mora.application.chain.chain_builder import build_proceso_chain
from cartera_mora.application.chain.handler import Handler
from cartera_mora.application.chain.proceso_context import ProcesoContext
from cartera_mora.domain.ports.cartera_repository import CarteraRepositoryPort
from cartera_mora.domain.ports.credito_repository import CreditoRepositoryPort
from cartera_mora.domain.ports.manifiesto_repository import ManifiestoRepositoryPort
from cartera_mora.domain.ports.reporte_repository import ReporteRepositoryPort
from cartera_mora.domain.services.cartera_mora_service import CarteraMoraService
from cartera_mora.domain.services.cartera_merge_service import CarteraMergeService
from cartera_mora.domain.services.manifiesto_lis_service import ManifiestoLisService


@dataclass(frozen=True)
class ProcesarCarteraMoraResult:
    total_creditos_procesados: int
    total_en_mora: int
    total_saldo_mora: float
    archivo_reporte: Path
    archivo_lis: Path


class ProcesarCarteraMoraUseCase:
    """Caso de uso: procesa 2 archivos de entrada y genera JSON + LIS."""

    def __init__(
        self,
        proceso_chain: Handler,
        dias_mora_minimo: int,
        archivo_morosidad: Path,
        archivo_cartera: Path,
        archivo_reporte: Path,
        archivo_lis: Path,
    ) -> None:
        self._proceso_chain = proceso_chain
        self._dias_mora_minimo = dias_mora_minimo
        self._archivo_morosidad = archivo_morosidad
        self._archivo_cartera = archivo_cartera
        self._archivo_reporte = archivo_reporte
        self._archivo_lis = archivo_lis

    @classmethod
    def crear(
        cls,
        morosidad_repository: CreditoRepositoryPort,
        cartera_repository: CarteraRepositoryPort,
        reporte_repository: ReporteRepositoryPort,
        manifiesto_repository: ManifiestoRepositoryPort,
        cartera_mora_service: CarteraMoraService,
        cartera_merge_service: CarteraMergeService,
        manifiesto_lis_service: ManifiestoLisService,
        dias_mora_minimo: int,
        archivo_morosidad: Path,
        archivo_cartera: Path,
        archivo_reporte: Path,
        archivo_lis: Path,
    ) -> "ProcesarCarteraMoraUseCase":
        chain = build_proceso_chain(
            morosidad_repository=morosidad_repository,
            cartera_repository=cartera_repository,
            reporte_repository=reporte_repository,
            manifiesto_repository=manifiesto_repository,
            cartera_mora_service=cartera_mora_service,
            cartera_merge_service=cartera_merge_service,
            manifiesto_lis_service=manifiesto_lis_service,
        )
        return cls(
            proceso_chain=chain,
            dias_mora_minimo=dias_mora_minimo,
            archivo_morosidad=archivo_morosidad,
            archivo_cartera=archivo_cartera,
            archivo_reporte=archivo_reporte,
            archivo_lis=archivo_lis,
        )

    def ejecutar(self) -> ProcesarCarteraMoraResult:
        contexto = ProcesoContext(
            dias_mora_minimo=self._dias_mora_minimo,
            archivo_morosidad=self._archivo_morosidad,
            archivo_cartera=self._archivo_cartera,
            archivo_reporte=self._archivo_reporte,
            archivo_lis=self._archivo_lis,
        )
        contexto_final = self._proceso_chain.manejar(contexto)
        reporte = contexto_final.reporte

        return ProcesarCarteraMoraResult(
            total_creditos_procesados=len(contexto_final.creditos),
            total_en_mora=reporte["total_creditos"],
            total_saldo_mora=reporte["total_saldo_mora"],
            archivo_reporte=self._archivo_reporte,
            archivo_lis=self._archivo_lis,
        )
