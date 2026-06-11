import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional

from cobranzas.domain.models.asignacion_credito import AsignacionCredito

logger = logging.getLogger("cobranzas.asignacion.export")

COLUMNAS_CSV = ("ID_CREDITO", "USUARIO")


def _csv_tiene_filas_datos(ruta: Path) -> bool:
    if not ruta.is_file():
        return False
    with ruta.open(encoding="utf-8-sig", newline="") as fh:
        return any(True for _ in csv.DictReader(fh))


class ExportarAsignacionService:
    def exportar_csv(
        self,
        ruta: Path,
        asignaciones: List[AsignacionCredito],
        ids_recblue_por_operacion: Optional[Dict[str, str]] = None,
        solo_nuevas: bool = True,
    ) -> None:
        """
        Entregable: ID_CREDITO (export Recblue) + USUARIO (nombre asesor en BD).

        Por defecto solo exporta asignaciones nuevas del día (reasignado=True).
        Omite filas sin ID Crédito en Recblue.

        Si no hay filas nuevas y el CSV del día ya existe con datos, no se
        sobrescribe (p. ej. re-ejecutar el 5-jun tras correr el 6-jun).
        """
        mapa = ids_recblue_por_operacion or {}
        filas_export: List[Dict[str, str]] = []
        omitidas = 0
        conservadas = 0

        for fila in asignaciones:
            if solo_nuevas and not fila.reasignado:
                conservadas += 1
                continue
            id_credito = (
                mapa.get(fila.numero_operacion) or fila.id_credito_recblue or ""
            ).strip()
            if not id_credito:
                omitidas += 1
                continue
            filas_export.append(
                {
                    "ID_CREDITO": id_credito,
                    "USUARIO": fila.nombre_asesor or fila.codigo_asesor,
                }
            )

        if not filas_export:
            if _csv_tiene_filas_datos(ruta):
                logger.info(
                    "ASIGNACION.csv sin cambios: %s (0 nuevas; se conserva el archivo)",
                    ruta,
                )
                return
            logger.info(
                "ASIGNACION.csv omitido: %s (0 nuevas; sin archivo previo)",
                ruta,
            )
            return

        ruta.parent.mkdir(parents=True, exist_ok=True)
        exportadas = len(filas_export)
        with ruta.open("w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=COLUMNAS_CSV)
            writer.writeheader()
            writer.writerows(filas_export)

        if omitidas:
            logger.warning(
                "ASIGNACION.csv: %s filas sin ID Crédito Recblue (omitidas)",
                omitidas,
            )
        logger.info(
            "ASIGNACION.csv generado: %s (%s nuevas, %s conservadas BD, %s sin Recblue)",
            ruta,
            exportadas,
            conservadas,
            omitidas,
        )
