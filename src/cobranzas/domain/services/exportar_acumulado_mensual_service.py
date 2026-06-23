"""Genera el Excel acumulado mensual desde deuda + asesores_deuda."""

import logging
from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Set

from cobranzas.domain.models.fila_acumulado_mensual import FilaAcumuladoMensual
from cobranzas.domain.ports.acumulado_excel_port import AcumuladoExcelPort
from cobranzas.domain.ports.acumulado_mensual_port import AcumuladoMensualPort
from cobranzas.domain.services.dias_habiles_service import fecha_consulta_mora
from cobranzas.infrastructure.config.entregables_mensuales import ruta_acumulado_mensual

logger = logging.getLogger(__name__)

# Acumulado mensual: solo operaciones con días de mora >= este valor (2 = más de 1 día).
DIAS_MORA_MINIMO_ACUMULADO_DEFAULT = 2


def _dias_mora_efectivos(fila: FilaAcumuladoMensual) -> int:
    """Días de mora a evaluar: CAMOROSICO con prioridad; si no, dias_mora."""
    if fila.dias_atraso_camorosico is not None:
        return fila.dias_atraso_camorosico
    return fila.dias_mora or 0


class ExportarAcumuladoMensualService:
    def __init__(
        self,
        acumulado_repository: AcumuladoMensualPort,
        excel_writer: AcumuladoExcelPort,
        directorio_destino: Path,
        dias_mora_minimo: int = DIAS_MORA_MINIMO_ACUMULADO_DEFAULT,
    ) -> None:
        self._acumulado = acumulado_repository
        self._excel = excel_writer
        self._directorio_destino = directorio_destino
        self._dias_mora_minimo = (
            dias_mora_minimo
            if dias_mora_minimo and dias_mora_minimo > 0
            else DIAS_MORA_MINIMO_ACUMULADO_DEFAULT
        )

    def exportar(
        self,
        fecha_archivo: date,
        feriados: Set[date],
        es_fin_de_mes: bool = False,
    ) -> Path:
        """
        Lee el lote por fecha del archivo (.lis) y escribe en Excel la fecha de proceso
        (consulta efectiva: día hábil siguiente al archivo).

        En el proceso diario el acumulado refleja TODO lo asignado (mora temprana,
        piso de 1 día). El filtro de días de mora >= ``dias_mora_minimo``
        (default 2, es decir más de 1 día) solo se aplica en fin de mes.
        """
        fecha_proceso = fecha_consulta_mora(fecha_archivo, feriados)
        archivo = ruta_acumulado_mensual(self._directorio_destino, fecha_proceso)
        filas_bd = self._acumulado.filas_por_fecha_corte(fecha_archivo)
        if not filas_bd:
            logger.info(
                "Acumulado mensual omitido | archivo=%s | sin filas en BD",
                fecha_archivo.isoformat(),
            )
            return archivo

        dias_minimo = self._dias_mora_minimo if es_fin_de_mes else 1
        total_bd = len(filas_bd)
        filas_filtradas = [
            fila for fila in filas_bd if _dias_mora_efectivos(fila) >= dias_minimo
        ]
        descartadas = total_bd - len(filas_filtradas)
        if not filas_filtradas:
            logger.info(
                "Acumulado mensual omitido | archivo=%s | %s filas descartadas "
                "por días de mora < %s",
                fecha_archivo.isoformat(),
                descartadas,
                dias_minimo,
            )
            return archivo

        filas = [
            replace(fila, fecha_proceso=fecha_proceso) for fila in filas_filtradas
        ]
        escritas = self._excel.anexar_lote(archivo, fecha_archivo, filas)
        logger.info(
            "Acumulado mensual | archivo=%s | proceso=%s | filas=%s "
            "| fin_de_mes=%s | descartadas_dias<%s=%s | %s",
            fecha_archivo.isoformat(),
            fecha_proceso.isoformat(),
            escritas,
            es_fin_de_mes,
            dias_minimo,
            descartadas,
            archivo,
        )
        return archivo
