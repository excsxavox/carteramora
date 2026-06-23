from pathlib import Path
from typing import Optional

from cobranzas.application.chain.asignacion_handler import AsignacionHandler
from cobranzas.application.chain.exclusion_fin_mes_handler import ExclusionFinMesHandler
from cobranzas.application.chain.export_acumulado_handler import ExportAcumuladoHandler
from cobranzas.application.chain.export_asignacion_handler import ExportAsignacionHandler
from cobranzas.application.chain.handler import Handler
from cobranzas.application.chain.lectura_cartera_handler import LecturaCarteraHandler
from cobranzas.application.chain.lectura_morosidad_handler import LecturaMorosidadHandler
from cobranzas.application.chain.mora_temprana_handler import MoraTempranaHandler
from cobranzas.application.chain.persistencia_bd_handler import PersistenciaBDHandler
from cobranzas.application.chain.recblue_handler import (
    RecblueEnriquecimientoHandler,
    RecblueValidacionHandler,
)
from cobranzas.application.chain.reporte_handler import ProcesamientoMoraHandler
from cobranzas.domain.ports.cartera_repository import CarteraRepositoryPort
from cobranzas.domain.ports.credito_repository import CreditoRepositoryPort
from cobranzas.domain.ports.feriados_calendario_port import FeriadosCalendarioPort
from cobranzas.domain.ports.operaciones_fin_mes_port import OperacionesFinMesPort
from cobranzas.domain.services.asignacion_cartera_service import AsignacionCarteraService
from cobranzas.domain.services.cobranzas_service import CobranzasService
from cobranzas.domain.services.cartera_merge_service import CarteraMergeService
from cobranzas.domain.services.exportar_acumulado_mensual_service import (
    ExportarAcumuladoMensualService,
)
from cobranzas.domain.services.exportar_asignacion_service import ExportarAsignacionService
from cobranzas.domain.services.mora_temprana_service import MoraTempranaService
from cobranzas.domain.services.resolver_reglas_mora_service import (
    ResolverReglasMoraService,
)
from cobranzas.domain.services.persistir_cartera_mora_service import (
    PersistirCarteraMoraService,
)
from cobranzas.domain.services.tab_detalle_export_service import (
    TabDetalleExportService,
)
from cobranzas.infrastructure.adapters.recblue_archivo_adapter import RecblueArchivoAdapter


def build_proceso_chain(
    morosidad_repository: CreditoRepositoryPort,
    cartera_repository: CarteraRepositoryPort,
    cobranzas_service: CobranzasService,
    cartera_merge_service: CarteraMergeService,
    tab_detalle_export_service: Optional[TabDetalleExportService] = None,
    persistir_service: Optional[PersistirCarteraMoraService] = None,
    usar_mora_temprana: bool = False,
    feriados_repository: Optional[FeriadosCalendarioPort] = None,
    reglas_resolver: Optional[ResolverReglasMoraService] = None,
    asignacion_service: Optional[AsignacionCarteraService] = None,
    recblue_adapter: Optional[RecblueArchivoAdapter] = None,
    export_acumulado_service: Optional[ExportarAcumuladoMensualService] = None,
    directorio_destino: Optional[Path] = None,
    operaciones_fin_mes: Optional[OperacionesFinMesPort] = None,
) -> Handler:
    """
    morosidad → cartera → [Recblue] → [mora temprana → asignación]
    → reporte → [Recblue enrich] → [ASIGNACION.csv] → BD.
    """
    morosidad = LecturaMorosidadHandler(morosidad_repository)
    cadena: Handler = morosidad.enlazar(
        LecturaCarteraHandler(cartera_repository, cartera_merge_service)
    )

    if recblue_adapter is not None:
        cadena = cadena.enlazar(RecblueValidacionHandler(recblue_adapter))

    if (
        usar_mora_temprana
        and feriados_repository is not None
        and reglas_resolver is not None
    ):
        cadena = cadena.enlazar(
            MoraTempranaHandler(
                MoraTempranaService(),
                feriados_repository,
                reglas_resolver,
            )
        )
        if operaciones_fin_mes is not None:
            cadena = cadena.enlazar(ExclusionFinMesHandler(operaciones_fin_mes))
        if asignacion_service is not None:
            cadena = cadena.enlazar(AsignacionHandler(asignacion_service))

    cadena = cadena.enlazar(
        ProcesamientoMoraHandler(
            cobranzas_service,
            tab_detalle_export_service or TabDetalleExportService(),
        )
    )

    if recblue_adapter is not None:
        cadena = cadena.enlazar(RecblueEnriquecimientoHandler(recblue_adapter))

    if usar_mora_temprana and asignacion_service is not None:
        cadena = cadena.enlazar(
            ExportAsignacionHandler(
                ExportarAsignacionService(),
                feriados_repository,
                directorio_destino,
            )
        )

    if persistir_service is not None:
        cadena = cadena.enlazar(PersistenciaBDHandler(persistir_service))

    if export_acumulado_service is not None:
        cadena.enlazar(
            ExportAcumuladoHandler(export_acumulado_service, feriados_repository)
        )

    return morosidad
