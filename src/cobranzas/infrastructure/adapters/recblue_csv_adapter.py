import csv
import logging
from pathlib import Path
from typing import Dict, Optional

from cobranzas.domain.ports.recblue_port import RecbluePort

logger = logging.getLogger("cobranzas.recblue")

CLAVES_OPERACION = (
    "numero_operacion",
    "numero operacion",
    "no_operacion",
    "no.operacion",
    "operacion",
)
CLAVES_ID = (
    "id_credito",
    "id credito",
    "id_credito_recblue",
    "id",
)


def _normalizar_clave(nombre: str) -> str:
    return (nombre or "").strip().lower().replace(" ", "_")


class RecblueCsvAdapter(RecbluePort):
    def __init__(self, archivo: Optional[Path]) -> None:
        self._archivo = archivo

    def id_credito_por_operacion(self) -> Dict[str, str]:
        if self._archivo is None or not self._archivo.is_file():
            return {}

        with self._archivo.open(encoding="utf-8-sig", newline="") as fh:
            lector = csv.DictReader(fh)
            if not lector.fieldnames:
                return {}

            columnas = {_normalizar_clave(c): c for c in lector.fieldnames}
            col_op = next(
                (columnas[k] for k in CLAVES_OPERACION if k in columnas), None
            )
            col_id = next((columnas[k] for k in CLAVES_ID if k in columnas), None)
            if not col_op or not col_id:
                logger.warning(
                    "Recblue sin columnas esperadas en %s: %s",
                    self._archivo,
                    lector.fieldnames,
                )
                return {}

            mapa: Dict[str, str] = {}
            for fila in lector:
                operacion = (fila.get(col_op) or "").strip()
                id_credito = (fila.get(col_id) or "").strip()
                if operacion and id_credito:
                    mapa[operacion] = id_credito

        logger.info("Recblue cargado: %s operaciones desde %s", len(mapa), self._archivo)
        return mapa
