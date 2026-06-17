"""Cadena fin de mes: morosidad + cartera + Recblue → limpieza → acumulado (sin asignación)."""

from datetime import date
from pathlib import Path
from typing import Optional, Set

from cobranzas.application.chain.export_acumulado_fin_mes_handler import (
    ExportAcumuladoFinMesHandler,
)
from cobranzas.application.chain.handler import Handler
from cobranzas.application.chain.lectura_cartera_handler import LecturaCarteraHandler
from cobranzas.application.chain.lectura_morosidad_handler import LecturaMorosidadHandler
from cobranzas.application.chain.recblue_handler import RecblueEnriquecimientoHandler
from cobranzas.application.chain.reporte_handler import ProcesamientoMoraHandler
from cobranzas.domain.ports.cartera_repository import CarteraRepositoryPort
from cobranzas.domain.ports.credito_repository import CreditoRepositoryPort
from cobranzas.domain.services.cartera_merge_service import CarteraMergeService
from cobranzas.domain.services.cobranzas_service import CobranzasService
from cobranzas.domain.services.exportar_acumulado_fin_mes_service import (
    ExportarAcumuladoFinMesService,
)
from cobranzas.domain.services.tab_detalle_export_service import TabDetalleExportService
from cobranzas.infrastructure.adapters.recblue_archivo_adapter import RecblueArchivoAdapter


def build_fin_mes_chain(
    morosidad_repository: CreditoRepositoryPort,
    cartera_repository: CarteraRepositoryPort,
    cobranzas_service: CobranzasService,
    cartera_merge_service: CarteraMergeService,
    export_fin_mes_service: ExportarAcumuladoFinMesService,
    feriados: Set[date],
    tab_detalle_export_service: Optional[TabDetalleExportService] = None,
    recblue_adapter: Optional[RecblueArchivoAdapter] = None,
) -> Handler:
    """
    morosidad → cartera (merge) → reporte (.lis)
    → [Recblue enrich] → acumulado_fin_mes.xlsx
    """
    morosidad = LecturaMorosidadHandler(morosidad_repository)
    cadena: Handler = morosidad.enlazar(
        LecturaCarteraHandler(cartera_repository, cartera_merge_service)
    )

    cadena = cadena.enlazar(
        ProcesamientoMoraHandler(
            cobranzas_service,
            tab_detalle_export_service or TabDetalleExportService(),
        )
    )

    if recblue_adapter is not None:
        cadena = cadena.enlazar(RecblueEnriquecimientoHandler(recblue_adapter))

    cadena.enlazar(
        ExportAcumuladoFinMesHandler(export_fin_mes_service, feriados)
    )

    return morosidad
