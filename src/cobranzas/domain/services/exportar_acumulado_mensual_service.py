"""Genera el Excel acumulado mensual desde deuda + asesores_deuda."""

import logging
from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Set

from cobranzas.domain.ports.acumulado_excel_port import AcumuladoExcelPort
from cobranzas.domain.ports.acumulado_mensual_port import AcumuladoMensualPort
from cobranzas.domain.services.dias_habiles_service import fecha_consulta_mora
from cobranzas.infrastructure.config.entregables_mensuales import ruta_acumulado_mensual

logger = logging.getLogger(__name__)


class ExportarAcumuladoMensualService:
    def __init__(
        self,
        acumulado_repository: AcumuladoMensualPort,
        excel_writer: AcumuladoExcelPort,
        directorio_destino: Path,
    ) -> None:
        self._acumulado = acumulado_repository
        self._excel = excel_writer
        self._directorio_destino = directorio_destino

    def exportar(self, fecha_archivo: date, feriados: Set[date]) -> Path:
        """
        Lee el lote por fecha del archivo (.lis) y escribe en Excel la fecha de proceso
        (consulta efectiva: día hábil siguiente al archivo).
        """
        fecha_proceso = fecha_consulta_mora(fecha_archivo, feriados)
        archivo = ruta_acumulado_mensual(self._directorio_destino, fecha_archivo)
        filas_bd = self._acumulado.filas_por_fecha_corte(fecha_archivo)
        if not filas_bd:
            logger.info(
                "Acumulado mensual omitido | archivo=%s | sin filas en BD",
                fecha_archivo.isoformat(),
            )
            return archivo

        filas = [
            replace(fila, fecha_proceso=fecha_proceso) for fila in filas_bd
        ]
        escritas = self._excel.anexar_lote(archivo, fecha_archivo, filas)
        logger.info(
            "Acumulado mensual | archivo=%s | proceso=%s | filas=%s | %s",
            fecha_archivo.isoformat(),
            fecha_proceso.isoformat(),
            escritas,
            archivo,
        )
        return archivo
