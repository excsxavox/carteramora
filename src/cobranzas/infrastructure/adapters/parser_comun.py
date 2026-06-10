import re
from datetime import date, datetime
from pathlib import Path
from typing import List, Mapping, Optional, Sequence

CORTE_PATTERN = re.compile(r"CORTE\s+A:\s*(.+)", re.IGNORECASE)
TAB_DELIMITER = "\t"
ENCODINGS_LECTURA = ("utf-8", "utf-8-sig", "cp1252", "latin-1")


def leer_lineas_archivo(file_path: Path) -> List[str]:
    """Lee archivo .lis/.txt probando UTF-8 y codificaciones Windows (cp1252)."""
    contenido = file_path.read_bytes()
    for encoding in ENCODINGS_LECTURA:
        try:
            return contenido.decode(encoding).splitlines()
        except UnicodeDecodeError:
            continue
    return contenido.decode("latin-1", errors="replace").splitlines()


def parse_fecha_corte(line: str) -> date:
    """Fecha en línea CORTE A: del core (mes/día/año, igual que MMDDYYYY del POST)."""
    match = CORTE_PATTERN.search(line)
    if not match:
        raise ValueError(f"Línea de corte inválida: {line}")
    return datetime.strptime(match.group(1).strip(), "%m/%d/%Y").date()


def parse_float(value: str) -> float:
    cleaned = (value or "").strip().replace(",", "")
    if not cleaned:
        return 0.0
    return float(cleaned)


def parse_str(value: str) -> str:
    if value is None:
        return ""
    return str(value).strip()


def parse_int(value: str) -> int:
    cleaned = (value or "").strip()
    if not cleaned:
        return 0
    return int(float(cleaned))


def parse_int_seguro(value: str) -> Optional[int]:
    """Devuelve None si el valor no es numérico (filas con columnas desalineadas)."""
    cleaned = (value or "").strip().replace(",", "")
    if not cleaned:
        return 0
    try:
        return int(float(cleaned))
    except ValueError:
        return None


def es_numero_operacion(value: str) -> bool:
    operacion = parse_str(value)
    return bool(operacion) and operacion.isdigit()


def row_a_campos_tab(
    row: Mapping[str, str], fieldnames: Sequence[str]
) -> tuple[tuple[str, str], ...]:
    from cobranzas.domain.schemas.tab_schema import normalizar_encabezados

    columnas = normalizar_encabezados(fieldnames)
    return tuple(
        (columnas[i], parse_str(row.get(fieldnames[i], "")))
        for i in range(len(fieldnames))
    )
