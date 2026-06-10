import csv
from datetime import date
from pathlib import Path
from typing import List, Optional, Tuple

from cobranzas.domain.models.credito import Credito
from cobranzas.domain.schemas.tab_schema import normalizar_encabezados
from cobranzas.infrastructure.adapters.parser_comun import (
    TAB_DELIMITER,
    leer_lineas_archivo,
    parse_fecha_corte,
    parse_float,
    parse_int,
    parse_str,
    row_a_campos_tab,
)

MARCAS_CARTERA = (
    "TE DETALLADO DE CARTERA",
    "REPORTE DETALLADO DE CARTERA",
)
COL_NUMERO_OPERACION = "NUMERO OPERACION"
COL_NOMBRE = "NOMBRE"
COL_CEDULA = "CEDULA"
COL_SOCIO = "SOCIO"
COL_OFICINA = "DESC.OFICINA"
COL_DIAS_MORA = "DIAS MORA"
COL_ESTADO = "EST"
COL_SALDO_CAP_PREST = "SALDO CAP. PREST"
COL_TIPO_OPER = "TIPO OPER."
COL_TOTAL_OP = "TOTAL OP."
COL_CALIFICACION = "CALIFICAC"
COL_SEGMENTACION = "SEGMENTACION"
COL_FUENTE_REPAGO = "FUENTE REPAGO"
COL_OFICIAL = "OFICIAL"


def _row_to_credito(
    row: dict, fecha_corte: date, fieldnames: List[str]
) -> Credito:
    return Credito(
        id_credito=parse_str(row.get(COL_NUMERO_OPERACION)),
        cliente=parse_str(row.get(COL_NOMBRE)),
        saldo_pendiente=parse_float(row.get(COL_SALDO_CAP_PREST, "0")),
        dias_mora=parse_int(row.get(COL_DIAS_MORA, "0")),
        fecha_corte=fecha_corte,
        estado_operacion=parse_str(row.get(COL_ESTADO)),
        socio=parse_str(row.get(COL_SOCIO)),
        oficina=parse_str(row.get(COL_OFICINA)),
        cedula=parse_str(row.get(COL_CEDULA)),
        calificacion=parse_str(row.get(COL_CALIFICACION)),
        tipo_operacion=parse_str(row.get(COL_TIPO_OPER)),
        total_operacion=parse_float(row.get(COL_TOTAL_OP, "0")),
        segmentacion=parse_str(row.get(COL_SEGMENTACION)),
        fuente_repago=parse_str(row.get(COL_FUENTE_REPAGO)),
        codigo_oficial=parse_str(row.get(COL_OFICIAL)),
        campos_tab=row_a_campos_tab(row, fieldnames),
    )


def es_te_detallado_cartera(file_path: Path) -> bool:
    if not file_path.exists():
        return False
    primera_linea = leer_lineas_archivo(file_path)[0].upper()
    return any(marca in primera_linea for marca in MARCAS_CARTERA)


def leer_te_detallado_cartera(
    file_path: Path,
    fecha_corte_override: Optional[date] = None,
) -> Tuple[date, Tuple[str, ...], List[Credito]]:
    if not file_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {file_path}")

    lines = leer_lineas_archivo(file_path)
    fecha_corte: Optional[date] = None
    header_index: Optional[int] = None

    for index, line in enumerate(lines):
        if fecha_corte is None and "CORTE A:" in line.upper():
            fecha_corte = parse_fecha_corte(line)
        if COL_NUMERO_OPERACION in line and COL_DIAS_MORA in line:
            header_index = index
            break

    if fecha_corte_override is not None:
        fecha_corte = fecha_corte_override
    elif fecha_corte is None:
        raise ValueError("No se encontró la línea CORTE A: en el TE detallado de cartera")
    if header_index is None:
        raise ValueError("No se encontró la fila de encabezados del TE detallado de cartera")

    creditos: List[Credito] = []
    reader = csv.DictReader(lines[header_index:], delimiter=TAB_DELIMITER)
    fieldnames = list(reader.fieldnames or [])
    columnas_tab = normalizar_encabezados(fieldnames)

    for row in reader:
        if not parse_str(row.get(COL_NUMERO_OPERACION)):
            continue
        creditos.append(_row_to_credito(row, fecha_corte, fieldnames))

    return fecha_corte, columnas_tab, creditos
