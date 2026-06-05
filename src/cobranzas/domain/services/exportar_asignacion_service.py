import csv
import logging
from pathlib import Path
from typing import List

from cobranzas.domain.models.asignacion_credito import AsignacionCredito

logger = logging.getLogger("cobranzas.asignacion.export")

COLUMNAS_CSV = (
    "fecha_corte",
    "nombre",
    "identificacion",
    "socio",
    "numero_operacion",
    "saldo_capital",
    "dias_mora",
    "codigo_asesor",
    "nombre_asesor",
    "id_credito_recblue",
)


class ExportarAsignacionService:
    def exportar_csv(self, ruta: Path, asignaciones: List[AsignacionCredito]) -> None:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with ruta.open("w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=COLUMNAS_CSV)
            writer.writeheader()
            for fila in asignaciones:
                writer.writerow(
                    {
                        "fecha_corte": fila.fecha_corte.isoformat(),
                        "nombre": fila.nombre,
                        "identificacion": fila.identificacion,
                        "socio": fila.socio,
                        "numero_operacion": fila.numero_operacion,
                        "saldo_capital": f"{fila.saldo_capital:.2f}",
                        "dias_mora": fila.dias_mora,
                        "codigo_asesor": fila.codigo_asesor,
                        "nombre_asesor": fila.nombre_asesor,
                        "id_credito_recblue": fila.id_credito_recblue,
                    }
                )
        logger.info("ASIGNACION.csv generado: %s (%s filas)", ruta, len(asignaciones))
