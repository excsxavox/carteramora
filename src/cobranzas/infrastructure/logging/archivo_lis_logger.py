import json
import logging
from pathlib import Path
from typing import Dict, Sequence

from cobranzas.infrastructure.adapters.tab_lis_staging_reader import (
    TabArchivoParseado,
    extraer_numero_operacion,
    registrar_columnas,
)

logger = logging.getLogger("cobranzas.archivo.lis")

MAX_VALOR_LOG = 80
MAX_COLUMNAS_LISTADO = 50


class ArchivoLisLogger:
    """Logs del contenido leído desde .lis (columnas y valores del archivo)."""

    def __init__(self, muestra_filas: int = 3) -> None:
        self._muestra = max(0, muestra_filas)

    def log_inicio(self, archivo_morosidad: Path, archivo_mora: Path) -> None:
        logger.info("--- LECTURA ARCHIVOS .lis LIMPIOS ---")
        logger.info("Morosidad: %s", archivo_morosidad.as_posix())
        logger.info("Mora: %s", archivo_mora.as_posix())

    def log_archivo(self, ruta: Path, parseado: TabArchivoParseado) -> None:
        nombre = ruta.name
        columnas_info = registrar_columnas(
            parseado.encabezados_originales, parseado.columnas
        )
        total_filas = len(parseado.filas)

        logger.info("--- ARCHIVO: %s | %s filas | %s columnas ---", nombre, total_filas, len(columnas_info))
        self._log_listado_columnas(nombre, columnas_info)
        self._log_muestra_filas(nombre, parseado)

    def log_resumen_carga(
        self,
        id_lote: int,
        filas_morosidad: int,
        filas_mora: int,
    ) -> None:
        logger.info("--- CARGA STAGING lote=%s ---", id_lote)
        logger.info("  detalle_morosidad → tmp_stg_morosidad: %s filas", filas_morosidad)
        logger.info("  reporte_mora → tmp_stg_mora: %s filas", filas_mora)
        logger.info("--- FIN LECTURA ARCHIVOS ---")

    def _log_listado_columnas(
        self,
        nombre_archivo: str,
        columnas_info: Sequence[tuple],
    ) -> None:
        logger.info("  Columnas en %s:", nombre_archivo)
        for orden, nombre, original in columnas_info[:MAX_COLUMNAS_LISTADO]:
            if nombre == original:
                logger.info("    [%02d] %s", orden, nombre)
            else:
                logger.info("    [%02d] %s  (encabezado: %s)", orden, nombre, original)
        if len(columnas_info) > MAX_COLUMNAS_LISTADO:
            logger.info(
                "    ... +%s columnas (total %s)",
                len(columnas_info) - MAX_COLUMNAS_LISTADO,
                len(columnas_info),
            )

    def _log_muestra_filas(self, nombre_archivo: str, parseado: TabArchivoParseado) -> None:
        if self._muestra == 0:
            return
        total = len(parseado.filas)
        logger.info(
            "  Muestra de filas en %s (%s de %s):",
            nombre_archivo,
            min(self._muestra, total),
            total,
        )
        for idx, campos in enumerate(parseado.filas[: self._muestra]):
            numero_fila = idx + 2
            operacion = extraer_numero_operacion(campos) or "?"
            logger.info("    --- línea %s | no_operacion=%s ---", numero_fila, operacion)
            for columna in parseado.columnas:
                valor = (campos.get(columna) or "").strip()
                if not valor:
                    continue
                logger.info("      %s = %s", columna, self._truncar(valor))
            logger.debug(
                "      (json línea) %s",
                json.dumps(campos, ensure_ascii=False)[:2000],
            )
        if total > self._muestra:
            logger.info(
                "    ... %s líneas más (LOG_MUESTRA_MAPEO=%s)",
                total - self._muestra,
                self._muestra,
            )

    @staticmethod
    def _truncar(valor: str) -> str:
        if len(valor) <= MAX_VALOR_LOG:
            return repr(valor)
        return repr(valor[: MAX_VALOR_LOG - 3] + "...")
