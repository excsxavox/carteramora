"""Pipeline único: python main.py → todo el flujo diario."""

import logging
import sys
from typing import Optional

from cobranzas.application.chain.pipeline import PipelineContext, build_pipeline_chain
from cobranzas.domain.models.pipeline_run_result import PipelineRunResult
from cobranzas.infrastructure.config.database_url import resolver_database_url
from cobranzas.infrastructure.config.fecha_corte import fecha_corte_mmddyyyy
from cobranzas.infrastructure.config.fecha_corte import normalizar_fecha_corte
from cobranzas.infrastructure.config.settings import Settings
from cobranzas.infrastructure.persistence.database import (
    create_engine_from_settings,
    init_database,
    verificar_conexion,
)
from cobranzas.infrastructure.persistence.sqlite_schema_migrator import (
    migrar_sqlite_si_aplica,
)
from cobranzas.jobs.notificar_error import notificar_error_pipeline
from cobranzas.jobs.runner import _configure_logging

logger = logging.getLogger("cobranzas.pipeline")


def build_settings(
    fecha_corte: Optional[str] = None,
    es_fin_de_mes: Optional[bool] = None,
) -> Settings:
    """Settings desde .env; si hay fecha, resuelve rutas docsmora para ese día.

    ``es_fin_de_mes`` (si no es None) sobreescribe la bandera de fin de mes del .env.
    """
    import os

    overrides: dict = {
        "USAR_RUTAS_AUTOMATICAS": True,
        "DEFERIR_RESOLUCION_RUTAS": False,
    }
    if fecha_corte:
        overrides["FECHA_CORTE"] = normalizar_fecha_corte(fecha_corte)
    elif not os.getenv("FECHA_CORTE", "").strip():
        overrides["FECHA_CORTE"] = fecha_corte_mmddyyyy()
    if es_fin_de_mes is not None:
        overrides["ES_FIN_DE_MES"] = es_fin_de_mes
    return Settings(**overrides)


def _preparar_base_datos(settings: Settings) -> None:
    """Verifica conexión y crea tablas si no existen (sin migrar esquema)."""
    if not settings.persistir_en_bd and not settings.usar_mora_temprana:
        logger.info("Sin persistencia ni mora temprana: se omite init de BD")
        return

    engine = create_engine_from_settings(settings)
    init_database(engine)
    nuevas = migrar_sqlite_si_aplica(engine)
    if nuevas:
        logger.info("SQLite: %s columna(s) de esquema aplicada(s)", nuevas)
    verificar_conexion(engine)
    logger.info("Base de datos lista: %s", resolver_database_url(settings))


def _log_plan(settings: Settings) -> None:
    logger.info("=== Plan pipeline (python main.py) ===")
    if settings.usar_rutas_automaticas:
        logger.info(
            "Rutas automáticas | docsmora=%s | fecha=%s | lote=%s",
            settings.directorio_docsmora,
            settings.fecha_corte or "hoy",
            settings.archivo_morosidad.parent if settings.archivo_morosidad else "?",
        )
        logger.info("  CAMOROSICO → %s", settings.archivo_morosidad)
        logger.info("  CADETACACO → %s", settings.archivo_cartera)
    logger.info("1. Job 0  — Excel asesores → %s", settings.archivo_excel_asesores)
    logger.info(
        "2. Job 0b — Excel feriados → %s / %s (clave %s)",
        settings.directorio_excel_feriados,
        settings.patron_excel_feriados,
        settings.clave_feriados,
    )
    logger.info("3. Job 1  — Limpieza CAMOROSICO + CADETACACO")
    if settings.usar_mora_temprana:
        logger.info("         — Mora temprana, asignación, %s", settings.archivo_salida_asignacion)
    if settings.archivo_recblue:
        logger.info("         — Recblue: %s", settings.archivo_recblue)
    if settings.persistir_en_bd:
        logger.info("         — Persistencia BD (deudores, deuda, asesores_deuda)")
    if settings.incluir_staging_en_pipeline:
        logger.info("4. Job 2  — Staging tmp_* desde .lis limpios")


def _resultado_desde_contexto(
    settings: Settings, contexto: PipelineContext
) -> PipelineRunResult:
    ftxt = settings.fecha_corte or fecha_corte_mmddyyyy()
    limpieza = contexto.resultado_limpieza
    return PipelineRunResult(
        ok=contexto.codigo_salida == 0,
        codigo_salida=contexto.codigo_salida,
        fecha_corte=ftxt,
        archivo_morosidad=str(settings.archivo_morosidad),
        archivo_cartera=str(settings.archivo_cartera),
        archivo_salida_morosidad=str(settings.archivo_salida_morosidad),
        archivo_salida_mora=str(settings.archivo_salida_mora),
        archivo_asignacion=str(settings.archivo_salida_asignacion),
        archivo_acumulado_mensual=(
            str(limpieza.archivo_acumulado_mensual)
            if limpieza and limpieza.archivo_acumulado_mensual
            else None
        ),
        total_en_mora=limpieza.total_en_mora if limpieza else None,
        total_saldo_mora=limpieza.total_saldo_mora if limpieza else None,
        registros_persistidos_bd=limpieza.registros_persistidos_bd if limpieza else None,
        asignaciones_generadas=limpieza.asignaciones_generadas if limpieza else None,
        mensajes=list(contexto.mensajes),
    )


def ejecutar_pipeline(
    fecha_corte: Optional[str] = None,
    settings: Optional[Settings] = None,
    configurar_logs: bool = True,
    es_fin_de_mes: Optional[bool] = None,
) -> PipelineRunResult:
    """
    Ejecuta Jobs 0 + 0b + 1.

    :param fecha_corte: MMDDYYYY o YYYY-MM-DD; None = hoy (.env)
    :param es_fin_de_mes: si no es None, sobreescribe la bandera de fin de mes
    """
    cfg = settings or build_settings(fecha_corte, es_fin_de_mes=es_fin_de_mes)
    if configurar_logs:
        _configure_logging(cfg.log_level)

    _log_plan(cfg)
    _preparar_base_datos(cfg)

    contexto = PipelineContext(settings=cfg)
    contexto = build_pipeline_chain().manejar(contexto)

    if contexto.codigo_salida == 0:
        logger.info("=== Pipeline finalizado correctamente ===")
    else:
        logger.error("=== Pipeline detenido (código %s) ===", contexto.codigo_salida)
        for msg in contexto.mensajes:
            logger.error("  %s", msg)
        notificar_error_pipeline(
            cfg,
            origen="pipeline",
            mensajes=contexto.mensajes
            or [f"Pipeline detenido con código {contexto.codigo_salida}"],
            fecha_corte=cfg.fecha_corte or "",
        )

    return _resultado_desde_contexto(cfg, contexto)


def main() -> int:
    try:
        return ejecutar_pipeline().codigo_salida
    except Exception as exc:
        logger.exception("Error fatal en pipeline")
        try:
            cfg = build_settings()
            notificar_error_pipeline(
                cfg,
                origen="pipeline (error fatal)",
                mensajes=[str(exc)],
                fecha_corte=cfg.fecha_corte or "",
                exc=exc,
            )
        except Exception:
            logger.exception("No se pudo enviar notificación de error fatal")
        return 1


if __name__ == "__main__":
    sys.exit(main())
