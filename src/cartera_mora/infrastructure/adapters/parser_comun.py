import re
from datetime import date, datetime

CORTE_PATTERN = re.compile(r"CORTE\s+A:\s*(.+)", re.IGNORECASE)
TAB_DELIMITER = "\t"


def parse_fecha_corte(line: str) -> date:
    match = CORTE_PATTERN.search(line)
    if not match:
        raise ValueError(f"Línea de corte inválida: {line}")
    return datetime.strptime(match.group(1).strip(), "%d/%m/%Y").date()


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
