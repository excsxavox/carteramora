"""Nombres de columna genéricos para salidas TSV (.lis, manifiestos)."""

import re
from typing import Iterable, Sequence

TAB = "\t"

COL_ARCHIVO: Sequence[str] = ("tipo", "ruta", "descripcion", "registros")
COL_METADATO: Sequence[str] = ("campo", "valor")
COL_RESUMEN: Sequence[str] = ("campo", "valor")
COL_CLASIFICACION_MORA = "clasificacion_mora"


def normalizar_encabezado_tab(nombre: str) -> str:
    """Convierte encabezado del core a clave genérica snake_case para TSV."""
    texto = (nombre or "").strip().lower()
    texto = texto.replace(".", "_")
    texto = re.sub(r"[^\w]+", "_", texto, flags=re.UNICODE)
    texto = re.sub(r"_+", "_", texto).strip("_")
    return texto or "columna"


def normalizar_encabezados(originales: Sequence[str]) -> tuple[str, ...]:
    """Normaliza todos los encabezados; resuelve duplicados con sufijo _2, _3…"""
    vistos: dict[str, int] = {}
    resultado: list[str] = []
    for nombre in originales:
        base = normalizar_encabezado_tab(nombre)
        count = vistos.get(base, 0) + 1
        vistos[base] = count
        clave = base if count == 1 else f"{base}_{count}"
        resultado.append(clave)
    return tuple(resultado)


def unificar_columnas_tab(
    *grupos: Sequence[str],
    extra: Sequence[str] = (),
) -> tuple[str, ...]:
    """Orden estable sin duplicar columnas entre morosidad y cartera."""
    vistos: set[str] = set()
    resultado: list[str] = []
    for grupo in grupos:
        for columna in grupo:
            if columna not in vistos:
                vistos.add(columna)
                resultado.append(columna)
    for columna in extra:
        if columna not in vistos:
            vistos.add(columna)
            resultado.append(columna)
    return tuple(resultado)


def encabezado_tab(columnas: Sequence[str]) -> str:
    return TAB.join(columnas)


def fila_tab(valores: Iterable[object]) -> str:
    return TAB.join(str(v) for v in valores)