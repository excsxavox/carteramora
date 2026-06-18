"""Genera el Excel acumulado fin de mes: unificación CAMOROSICO + CADETACACO (sin filtro)."""

import logging
from datetime import date
from pathlib import Path
from typing import List, Set

from cobranzas.domain.models.credito import Credito
from cobranzas.domain.ports.acumulado_fin_mes_excel_port import AcumuladoFinMesExcelPort
from cobranzas.domain.services.dias_habiles_service import fecha_consulta_mora
from cobranzas.infrastructure.config.entregables_mensuales import ruta_acumulado_fin_mes
from cobranzas.infrastructure.persistence.mappers.acumulado_fin_mes_mapper import (
    credito_a_fila_acumulado_fin_mes,
)

logger = logging.getLogger(__name__)


class ExportarAcumuladoFinMesService:
    def __init__(
        self,
        excel_writer: AcumuladoFinMesExcelPort,
        directorio_destino: Path,
        dias_mora_minimo: int,
    ) -> None:
        self._excel = excel_writer
        self._directorio_destino = directorio_destino
        self._dias_mora_minimo = dias_mora_minimo

    def exportar(
        self,
        creditos: List[Credito],
        fecha_archivo: date,
        feriados: Set[date],
        archivo_origen: str = "",
    ) -> Path:
        fecha_proceso = fecha_consulta_mora(fecha_archivo, feriados)
        archivo = ruta_acumulado_fin_mes(self._directorio_destino, fecha_proceso)

        if not creditos:
            logger.info(
                "Acumulado fin mes omitido | archivo=%s | sin operaciones",
                fecha_archivo.isoformat(),
            )
            return archivo

        filas = [
            credito_a_fila_acumulado_fin_mes(
                credito,
                fecha_proceso,
                self._dias_mora_minimo,
                archivo_origen=archivo_origen,
            )
            for credito in creditos
        ]
        escritas = self._excel.anexar_lote(archivo, fecha_archivo, filas)
        logger.info(
            "Acumulado fin mes | archivo=%s | proceso=%s | filas=%s | %s",
            fecha_archivo.isoformat(),
            fecha_proceso.isoformat(),
            escritas,
            archivo,
        )
        return archivo
