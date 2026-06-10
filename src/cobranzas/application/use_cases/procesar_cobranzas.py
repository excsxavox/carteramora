from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from cobranzas.application.chain.chain_builder import build_proceso_chain
from cobranzas.application.chain.handler import Handler
from cobranzas.application.chain.proceso_context import ProcesoContext
from cobranzas.domain.ports.cartera_repository import CarteraRepositoryPort
from cobranzas.domain.ports.credito_repository import CreditoRepositoryPort
from cobranzas.domain.ports.feriados_calendario_port import FeriadosCalendarioPort
from cobranzas.domain.services.asignacion_cartera_service import AsignacionCarteraService
from cobranzas.infrastructure.adapters.recblue_archivo_adapter import RecblueArchivoAdapter
from cobranzas.domain.services.cobranzas_service import CobranzasService
from cobranzas.domain.services.cartera_merge_service import CarteraMergeService
from cobranzas.domain.services.exportar_acumulado_mensual_service import (
    ExportarAcumuladoMensualService,
)
from cobranzas.domain.services.persistir_cartera_mora_service import (
    PersistirCarteraMoraService,
)
from cobranzas.domain.services.resolver_reglas_mora_service import (
    ResolverReglasMoraService,
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
    archivo_asignacion: Path
    registros_persistidos_bd: int = 0
    asignaciones_generadas: int = 0
    archivo_acumulado_mensual: Optional[Path] = None


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
        usar_mora_temprana: bool = False,
        mora_temprana_dias_min: int = 1,
        mora_temprana_dias_max: int = 1,
        estados_excluidos: tuple[str, ...] = (),
        tipos_oper_excluidos: tuple[str, ...] = (),
        archivo_asignacion: Path = Path("destino/ASIGNACION.csv"),
        archivo_recblue: Optional[Path] = None,
    ) -> None:
        self._proceso_chain = proceso_chain
        self._dias_mora_minimo = dias_mora_minimo
        self._archivo_morosidad = archivo_morosidad
        self._archivo_cartera = archivo_cartera
        self._archivo_detalle_morosidad = archivo_detalle_morosidad
        self._archivo_detalle_mora = archivo_detalle_mora
        self._persistir_en_bd = persistir_en_bd
        self._database_url = database_url
        self._usar_mora_temprana = usar_mora_temprana
        self._mora_temprana_dias_min = mora_temprana_dias_min
        self._mora_temprana_dias_max = mora_temprana_dias_max
        self._estados_excluidos = estados_excluidos
        self._tipos_oper_excluidos = tipos_oper_excluidos
        self._archivo_asignacion = archivo_asignacion
        self._archivo_recblue = archivo_recblue

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
        usar_mora_temprana: bool = False,
        mora_temprana_dias_min: int = 1,
        mora_temprana_dias_max: int = 1,
        estados_excluidos: tuple[str, ...] = (),
        tipos_oper_excluidos: tuple[str, ...] = (),
        archivo_asignacion: Path = Path("destino/ASIGNACION.csv"),
        feriados_repository: Optional[FeriadosCalendarioPort] = None,
        reglas_resolver: Optional[ResolverReglasMoraService] = None,
        asignacion_service: Optional[AsignacionCarteraService] = None,
        recblue_adapter: Optional[RecblueArchivoAdapter] = None,
        archivo_recblue: Optional[Path] = None,
        export_acumulado_service: Optional[ExportarAcumuladoMensualService] = None,
    ) -> "ProcesarCobranzasUseCase":
        chain = build_proceso_chain(
            morosidad_repository=morosidad_repository,
            cartera_repository=cartera_repository,
            cobranzas_service=cobranzas_service,
            cartera_merge_service=cartera_merge_service,
            tab_detalle_export_service=tab_detalle_export_service,
            persistir_service=persistir_service,
            usar_mora_temprana=usar_mora_temprana,
            feriados_repository=feriados_repository,
            reglas_resolver=reglas_resolver,
            asignacion_service=asignacion_service,
            recblue_adapter=recblue_adapter,
            export_acumulado_service=export_acumulado_service,
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
            usar_mora_temprana=usar_mora_temprana,
            mora_temprana_dias_min=mora_temprana_dias_min,
            mora_temprana_dias_max=mora_temprana_dias_max,
            estados_excluidos=estados_excluidos,
            tipos_oper_excluidos=tipos_oper_excluidos,
            archivo_asignacion=archivo_asignacion,
            archivo_recblue=archivo_recblue,
        )

    def ejecutar(self) -> ProcesarCobranzasResult:
        contexto = ProcesoContext(
            dias_mora_minimo=self._dias_mora_minimo,
            usar_mora_temprana=self._usar_mora_temprana,
            mora_temprana_dias_min=self._mora_temprana_dias_min,
            mora_temprana_dias_max=self._mora_temprana_dias_max,
            estados_excluidos=self._estados_excluidos,
            tipos_oper_excluidos=self._tipos_oper_excluidos,
            archivo_morosidad=self._archivo_morosidad,
            archivo_cartera=self._archivo_cartera,
            archivo_detalle_morosidad=self._archivo_detalle_morosidad,
            archivo_detalle_mora=self._archivo_detalle_mora,
            archivo_asignacion=self._archivo_asignacion,
            archivo_recblue=self._archivo_recblue,
            validar_recblue=self._archivo_recblue is not None,
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
            archivo_asignacion=self._archivo_asignacion,
            registros_persistidos_bd=contexto_final.registros_persistidos_bd,
            asignaciones_generadas=len(contexto_final.asignaciones),
            archivo_acumulado_mensual=contexto_final.archivo_acumulado_mensual,
        )
