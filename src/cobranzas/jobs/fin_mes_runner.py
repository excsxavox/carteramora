"""Ejecuta limpieza + merge (camorosico, cadetacaco, Recblue) y acumulado fin de mes."""

import logging
from typing import Optional

from cobranzas.application.chain.fin_mes_chain_builder import build_fin_mes_chain
from cobranzas.application.chain.proceso_context import ProcesoContext
from cobranzas.domain.models.fin_mes_run_result import FinMesRunResult
from cobranzas.domain.services.cartera_merge_service import CarteraMergeService
from cobranzas.domain.services.cobranzas_service import CobranzasService
from cobranzas.domain.services.dias_habiles_service import fecha_consulta_mora
from cobranzas.domain.services.exportar_acumulado_fin_mes_service import (
    ExportarAcumuladoFinMesService,
)
from cobranzas.infrastructure.adapters.excel_acumulado_fin_mes_writer import (
    ExcelAcumuladoFinMesWriter,
)
from cobranzas.infrastructure.adapters.recblue_archivo_adapter import RecblueArchivoAdapter
from cobranzas.infrastructure.adapters.tsv_cartera_repository import TsvCarteraRepository
from cobranzas.infrastructure.adapters.tsv_credito_repository import TsvCreditoRepository
from cobranzas.infrastructure.config.feriados_excel_loader import cargar_feriados_desde_excel
from cobranzas.infrastructure.config.fecha_corte import fecha_corte_mmddyyyy
from cobranzas.infrastructure.config.settings import Settings
from cobranzas.jobs.pipeline_runner import build_settings
from cobranzas.jobs.runner import _configure_logging

logger = logging.getLogger("cobranzas.fin_mes")


def ejecutar_fin_mes(
    fecha_corte: Optional[str] = None,
    settings: Optional[Settings] = None,
    configurar_logs: bool = True,
) -> FinMesRunResult:
    """
    Limpia detalles, fusiona camorosico + cadetacaco (+ Recblue) y genera
    acumulado_fin_mes_{fecha proceso}.xlsx sin asignación ni BD.
    """
    cfg = settings or build_settings(fecha_corte)
    if configurar_logs:
        _configure_logging(cfg.log_level)

    feriados = cargar_feriados_desde_excel(cfg)
    fecha_archivo = cfg.fecha_corte_efectiva()
    fecha_proceso = fecha_consulta_mora(fecha_archivo, feriados)

    recblue_adapter = None
    if cfg.archivo_recblue is not None:
        recblue_adapter = RecblueArchivoAdapter(cfg.archivo_recblue)

    export_service = ExportarAcumuladoFinMesService(
        ExcelAcumuladoFinMesWriter(),
        cfg.directorio_destino,
        cfg.dias_mora_minimo,
    )

    chain = build_fin_mes_chain(
        morosidad_repository=TsvCreditoRepository(
            cfg.archivo_morosidad, fecha_corte=fecha_archivo
        ),
        cartera_repository=TsvCarteraRepository(
            cfg.archivo_cartera, fecha_corte=fecha_archivo
        ),
        cobranzas_service=CobranzasService(),
        cartera_merge_service=CarteraMergeService(),
        export_fin_mes_service=export_service,
        feriados=feriados,
        recblue_adapter=recblue_adapter,
    )

    contexto = ProcesoContext(
        dias_mora_minimo=cfg.dias_mora_minimo,
        usar_mora_temprana=False,
        archivo_morosidad=cfg.archivo_morosidad,
        archivo_cartera=cfg.archivo_cartera,
        archivo_detalle_morosidad=cfg.archivo_salida_morosidad,
        archivo_detalle_mora=cfg.archivo_salida_mora,
        archivo_recblue=cfg.archivo_recblue,
        validar_recblue=False,
        persistir_en_bd=False,
    )

    try:
        contexto_final = chain.manejar(contexto)
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        return FinMesRunResult(
            ok=False,
            codigo_salida=1,
            fecha_archivo=cfg.fecha_corte or fecha_corte_mmddyyyy(),
            fecha_proceso=fecha_corte_mmddyyyy(fecha_proceso),
            archivo_morosidad=str(cfg.archivo_morosidad),
            archivo_cartera=str(cfg.archivo_cartera),
            archivo_detalle_morosidad=str(cfg.archivo_salida_morosidad),
            archivo_detalle_mora=str(cfg.archivo_salida_mora),
            archivo_acumulado_fin_mes=None,
            total_en_mora=0,
            total_saldo_mora=0.0,
            filas_acumulado=0,
            mensajes=(str(exc),),
        )

    reporte = contexto_final.reporte
    archivo_fin_mes = getattr(contexto_final, "archivo_acumulado_fin_mes", None)
    filas = len(contexto_final.creditos)

    logger.info(
        "Fin mes OK | archivo=%s | proceso=%s | unificadas=%s | acumulado=%s",
        fecha_archivo.isoformat(),
        fecha_proceso.isoformat(),
        filas,
        archivo_fin_mes,
    )

    return FinMesRunResult(
        ok=True,
        codigo_salida=0,
        fecha_archivo=cfg.fecha_corte or fecha_corte_mmddyyyy(),
        fecha_proceso=fecha_corte_mmddyyyy(fecha_proceso),
        archivo_morosidad=str(cfg.archivo_morosidad),
        archivo_cartera=str(cfg.archivo_cartera),
        archivo_detalle_morosidad=str(cfg.archivo_salida_morosidad),
        archivo_detalle_mora=str(cfg.archivo_salida_mora),
        archivo_acumulado_fin_mes=str(archivo_fin_mes) if archivo_fin_mes else None,
        total_en_mora=reporte.get("total_creditos", filas),
        total_saldo_mora=float(reporte.get("total_saldo_mora", 0.0)),
        filas_acumulado=filas,
    )


def main() -> int:
    return ejecutar_fin_mes().codigo_salida


if __name__ == "__main__":
    raise SystemExit(main())
