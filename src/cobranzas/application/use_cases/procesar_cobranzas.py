from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from cobranzas.application.chain.chain_builder import build_proceso_chain
from cobranzas.application.chain.handler import Handler
from cobranzas.application.chain.proceso_context import ProcesoContext
from cobranzas.domain.ports.cartera_repository import CarteraRepositoryPort
from cobranzas.domain.ports.credito_repository import CreditoRepositoryPort
from cobranzas.domain.services.cobranzas_service import CobranzasService
from cobranzas.domain.services.cartera_merge_service import CarteraMergeService
from cobranzas.domain.services.persistir_cartera_mora_service import (
    PersistirCarteraMoraService,
)
from cobranzas.domain.services.tab_detalle_export_service import (
    TabDetalleExportService,
)


@dataclass(frozen=True)
class ProcesarCobranzasResult:
    total_creditos_procesados: int
    total_en_mora: int
    total_saldo_mora: float
    archivo_detalle_morosidad: Path
    archivo_detalle_mora: Path
    registros_persistidos_bd: int = 0


class ProcesarCobranzasUseCase:
    """Caso de uso: procesa 2 archivos de entrada y genera 2 archivos .lis."""

    def __init__(
        self,
        proceso_chain: Handler,
        dias_mora_minimo: int,
        archivo_morosidad: Path,
        archivo_cartera: Path,
        archivo_detalle_morosidad: Path,
        archivo_detalle_mora: Path,
        persistir_en_bd: bool = False,
        database_url: str = "",
    ) -> None:
        self._proceso_chain = proceso_chain
        self._dias_mora_minimo = dias_mora_minimo
        self._archivo_morosidad = archivo_morosidad
        self._archivo_cartera = archivo_cartera
        self._archivo_detalle_morosidad = archivo_detalle_morosidad
        self._archivo_detalle_mora = archivo_detalle_mora
        self._persistir_en_bd = persistir_en_bd
        self._database_url = database_url

    @classmethod
    def crear(
        cls,
        morosidad_repository: CreditoRepositoryPort,
        cartera_repository: CarteraRepositoryPort,
        cobranzas_service: CobranzasService,
        cartera_merge_service: CarteraMergeService,
        dias_mora_minimo: int,
        archivo_morosidad: Path,
        archivo_cartera: Path,
        archivo_detalle_morosidad: Path,
        archivo_detalle_mora: Path,
        tab_detalle_export_service: Optional[TabDetalleExportService] = None,
        persistir_service: Optional[PersistirCarteraMoraService] = None,
        persistir_en_bd: bool = False,
        database_url: str = "",
    ) -> "ProcesarCobranzasUseCase":
        chain = build_proceso_chain(
            morosidad_repository=morosidad_repository,
            cartera_repository=cartera_repository,
            cobranzas_service=cobranzas_service,
            cartera_merge_service=cartera_merge_service,
            tab_detalle_export_service=tab_detalle_export_service,
            persistir_service=persistir_service,
        )
        return cls(
            proceso_chain=chain,
            dias_mora_minimo=dias_mora_minimo,
            archivo_morosidad=archivo_morosidad,
            archivo_cartera=archivo_cartera,
            archivo_detalle_morosidad=archivo_detalle_morosidad,
            archivo_detalle_mora=archivo_detalle_mora,
            persistir_en_bd=persistir_en_bd,
            database_url=database_url,
        )

    def ejecutar(self) -> ProcesarCobranzasResult:
        contexto = ProcesoContext(
            dias_mora_minimo=self._dias_mora_minimo,
            archivo_morosidad=self._archivo_morosidad,
            archivo_cartera=self._archivo_cartera,
            archivo_detalle_morosidad=self._archivo_detalle_morosidad,
            archivo_detalle_mora=self._archivo_detalle_mora,
            persistir_en_bd=self._persistir_en_bd,
            database_url=self._database_url,
        )
        contexto_final = self._proceso_chain.manejar(contexto)
        reporte = contexto_final.reporte

        return ProcesarCobranzasResult(
            total_creditos_procesados=len(contexto_final.creditos),
            total_en_mora=reporte["total_creditos"],
            total_saldo_mora=reporte["total_saldo_mora"],
            archivo_detalle_morosidad=self._archivo_detalle_morosidad,
            archivo_detalle_mora=self._archivo_detalle_mora,
            registros_persistidos_bd=contexto_final.registros_persistidos_bd,
        )
