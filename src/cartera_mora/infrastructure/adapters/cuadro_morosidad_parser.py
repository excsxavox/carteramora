import csv
from datetime import date
from pathlib import Path
from typing import List, Optional, Tuple

from cartera_mora.domain.models.credito import Credito
from cartera_mora.infrastructure.adapters.parser_comun import (
    TAB_DELIMITER,
    parse_fecha_corte,
    parse_float,
    parse_int,
    parse_str,
)

MARCA_CUADRO = "CUADRO DE MOROSIDAD"
COL_NO_OPERACION = "NO.OPERACION"
COL_NOMBRE_SOCIO = "NOMBRE SOCIO"
COL_DIAS_ATRASO = "DIAS ATRASO"
COL_SALDO_CAPITAL_ATRASADO = "SALDO CAPITAL ATRASADO"
COL_SALDO_CAPITAL_PREST = "SALDO CAPITAL PREST."
COL_ESTADO = "ESTADO"
COL_SOCIO = "SOCIO"
COL_OFICINA = "DES.OFICINA"
COL_NOMBRE_OFICIAL = "NOMBRE OFICIAL"
COL_TIPO_OPER = "TIPO OPER."
COL_TOTAL_ATRASADO = "TOTAL ATRASADO"


def _row_to_credito(row: dict, fecha_corte: date) -> Credito:
    saldo_atrasado = parse_float(row.get(COL_SALDO_CAPITAL_ATRASADO, "0"))
    saldo_prestamo = parse_float(row.get(COL_SALDO_CAPITAL_PREST, "0"))
    return Credito(
        id_credito=parse_str(row.get(COL_NO_OPERACION)),
        cliente=parse_str(row.get(COL_NOMBRE_SOCIO)),
        saldo_pendiente=saldo_atrasado if saldo_atrasado > 0 else saldo_prestamo,
        dias_mora=parse_int(row.get(COL_DIAS_ATRASO, "0")),
        fecha_corte=fecha_corte,
        estado_operacion=parse_str(row.get(COL_ESTADO)),
        socio=parse_str(row.get(COL_SOCIO)),
        oficina=parse_str(row.get(COL_OFICINA)),
        nombre_oficial=parse_str(row.get(COL_NOMBRE_OFICIAL)),
        tipo_operacion=parse_str(row.get(COL_TIPO_OPER)),
        total_atrasado=parse_float(row.get(COL_TOTAL_ATRASADO, "0")),
    )


def es_cuadro_morosidad(file_path: Path) -> bool:
    if not file_path.exists():
        return False
    primera_linea = file_path.read_text(encoding="utf-8").splitlines()[0]
    return MARCA_CUADRO in primera_linea.upper()


def leer_cuadro_morosidad(file_path: Path) -> Tuple[date, List[Credito]]:
    if not file_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {file_path}")

    lines = file_path.read_text(encoding="utf-8").splitlines()
    fecha_corte: Optional[date] = None
    header_index: Optional[int] = None

    for index, line in enumerate(lines):
        if fecha_corte is None and "CORTE A:" in line.upper():
            fecha_corte = parse_fecha_corte(line)
        if COL_NO_OPERACION in line and COL_DIAS_ATRASO in line:
            header_index = index
            break

    if fecha_corte is None:
        raise ValueError("No se encontró la línea CORTE A: en el cuadro de morosidad")
    if header_index is None:
        raise ValueError("No se encontró la fila de encabezados del cuadro de morosidad")

    creditos: List[Credito] = []
    reader = csv.DictReader(lines[header_index:], delimiter=TAB_DELIMITER)
    for row in reader:
        if not parse_str(row.get(COL_NO_OPERACION)):
            continue
        creditos.append(_row_to_credito(row, fecha_corte))

    return fecha_corte, creditos
