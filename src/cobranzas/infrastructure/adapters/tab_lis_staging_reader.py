import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from cobranzas.domain.schemas.tab_schema import TAB, normalizar_encabezados
from cobranzas.infrastructure.adapters.parser_comun import leer_lineas_archivo

CLAVES_NUMERO_OPERACION: Tuple[str, ...] = (
    "no_operacion",
    "numero_operacion",
    "no_operacion_2",
)


@dataclass(frozen=True)
class TabArchivoParseado:
    encabezados_originales: Tuple[str, ...]
    columnas: Tuple[str, ...]
    filas: Tuple[Dict[str, str], ...]


def parsear_archivo_tab(file_path: Path) -> TabArchivoParseado:
    """Lee .lis limpio: primera línea encabezados TAB, resto datos."""
    lineas = [ln for ln in leer_lineas_archivo(file_path) if ln.strip()]
    if not lineas:
        raise ValueError(f"Archivo vacío: {file_path}")

    originales = tuple(lineas[0].split(TAB))
    columnas = normalizar_encabezados(originales)
    filas: List[Dict[str, str]] = []

    for numero_fila, linea in enumerate(lineas[1:], start=2):
        valores = linea.split(TAB)
        if len(valores) < len(columnas):
            valores.extend([""] * (len(columnas) - len(valores)))
        elif len(valores) > len(columnas):
            valores = valores[: len(columnas)]
        filas.append(dict(zip(columnas, valores)))

    return TabArchivoParseado(
        encabezados_originales=originales,
        columnas=columnas,
        filas=tuple(filas),
    )


def extraer_numero_operacion(campos: Dict[str, str]) -> str:
    for clave in CLAVES_NUMERO_OPERACION:
        valor = (campos.get(clave) or "").strip()
        if valor:
            return valor
    return ""


def fila_a_json(campos: Dict[str, str]) -> str:
    return json.dumps(campos, ensure_ascii=False, separators=(",", ":"))


def registrar_columnas(
    originales: Sequence[str],
    columnas: Sequence[str],
) -> List[Tuple[int, str, str]]:
    """(orden, nombre_columna, nombre_original)."""
    return [
        (orden, columnas[orden], originales[orden] if orden < len(originales) else columnas[orden])
        for orden in range(len(columnas))
    ]
