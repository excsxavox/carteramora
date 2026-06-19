"""Conversión fiel de archivos .lis (tab-delimitados) a Excel (.xlsx).

Cada línea del .lis se vuelca como una fila; cada valor (separado por tab) en
una celda. Los valores se escriben como texto para preservar ceros a la
izquierda (p. ej. números de operación como 0012117441).
"""

from pathlib import Path
from typing import List

from openpyxl import Workbook
from openpyxl.cell.cell import WriteOnlyCell


def _leer_lineas(origen: Path) -> List[str]:
    try:
        texto = origen.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        texto = origen.read_text(encoding="latin-1")
    return texto.splitlines()


class LisExcelWriter:
    """Escribe un .lis tab-delimitado como .xlsx (una fila por línea)."""

    def convertir(self, origen: Path, destino: Path) -> int:
        lineas = _leer_lineas(origen)
        destino.parent.mkdir(parents=True, exist_ok=True)

        libro = Workbook(write_only=True)
        hoja = libro.create_sheet(title="Datos")
        filas = 0
        for linea in lineas:
            celdas = []
            for valor in linea.split("\t"):
                celda = WriteOnlyCell(hoja, value=valor)
                celda.data_type = "s"  # forzar texto, preserva ceros a la izquierda
                celdas.append(celda)
            hoja.append(celdas)
            filas += 1

        libro.save(destino)
        return filas
