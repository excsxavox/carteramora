import csv
from datetime import date
from pathlib import Path
from typing import List, Optional

from cobranzas.domain.models.credito import Credito
from cobranzas.infrastructure.adapters.cuadro_morosidad_parser import (
    es_cuadro_morosidad,
    leer_cuadro_morosidad,
)

TAB_DELIMITER = "\t"
CAMPOS_CREDITO = [
    "id_credito",
    "cliente",
    "saldo_pendiente",
    "dias_mora",
    "fecha_corte",
    "estado_operacion",
    "socio",
    "oficina",
]


def leer_creditos_tsv(
    file_path: Path, fecha_corte: Optional[date] = None
) -> List[Credito]:
    if not file_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {file_path}")

    if es_cuadro_morosidad(file_path):
        _, _, creditos = leer_cuadro_morosidad(
            file_path, fecha_corte_override=fecha_corte
        )
        return creditos

    creditos: List[Credito] = []
    with file_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=TAB_DELIMITER)
        for row in reader:
            creditos.append(
                Credito(
                    id_credito=row["id_credito"].strip(),
                    cliente=row["cliente"].strip(),
                    saldo_pendiente=float(row["saldo_pendiente"]),
                    dias_mora=int(row["dias_mora"]),
                    fecha_corte=date.fromisoformat(row["fecha_corte"]),
                    estado_operacion=row.get("estado_operacion", "").strip(),
                    socio=row.get("socio", "").strip(),
                    oficina=row.get("oficina", "").strip(),
                )
            )
    return creditos


def escribir_creditos_tsv(file_path: Path, creditos: List[Credito]) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_CREDITO, delimiter=TAB_DELIMITER)
        writer.writeheader()
        for credito in creditos:
            writer.writerow(
                {
                    "id_credito": credito.id_credito,
                    "cliente": credito.cliente,
                    "saldo_pendiente": credito.saldo_pendiente,
                    "dias_mora": credito.dias_mora,
                    "fecha_corte": credito.fecha_corte.isoformat(),
                    "estado_operacion": credito.estado_operacion,
                    "socio": credito.socio,
                    "oficina": credito.oficina,
                }
            )
