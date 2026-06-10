"""Genera el Excel acumulado mensual desde deuda + asesores_deuda."""

import logging
from datetime import date
from pathlib import Path

from cobranzas.domain.ports.acumulado_excel_port import AcumuladoExcelPort
from cobranzas.domain.ports.acumulado_mensual_port import AcumuladoMensualPort
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

    def exportar(self, fecha_corte: date) -> Path:
        archivo = ruta_acumulado_mensual(self._directorio_destino, fecha_corte)
        filas = self._acumulado.filas_por_fecha_corte(fecha_corte)
        if not filas:
            logger.info(
                "Acumulado mensual omitido | %s | sin filas en BD para fecha_corte",
                fecha_corte.isoformat(),
            )
            return archivo

        escritas = self._excel.anexar_lote(archivo, fecha_corte, filas)
        logger.info(
            "Acumulado mensual | %s | filas=%s | %s",
            fecha_corte.isoformat(),
            escritas,
            archivo,
        )
        return archivo
