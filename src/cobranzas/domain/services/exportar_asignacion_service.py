import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional

from cobranzas.domain.models.asignacion_credito import AsignacionCredito

logger = logging.getLogger("cobranzas.asignacion.export")

COLUMNAS_CSV = ("ID_CREDITO", "USUARIO")


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
        """
        ruta.parent.mkdir(parents=True, exist_ok=True)
        mapa = ids_recblue_por_operacion or {}
        exportadas = 0
        omitidas = 0
        conservadas = 0

        with ruta.open("w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=COLUMNAS_CSV)
            writer.writeheader()
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
                writer.writerow(
                    {
                        "ID_CREDITO": id_credito,
                        "USUARIO": fila.nombre_asesor or fila.codigo_asesor,
                    }
                )
                exportadas += 1

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
