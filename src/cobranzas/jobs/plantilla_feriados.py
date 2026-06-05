"""Genera data/catalogo/dias_feriados.xlsx (feriados nacionales Ecuador)."""

from pathlib import Path

from openpyxl import Workbook

from cobranzas.infrastructure.config.settings import Settings

# Feriados nacionales Ecuador — año calendario (descripción, inicio M/D/Y, fin opcional)
_FERIADOS_2026 = [
    ("Descripción", "Fecha inicio", "Fecha fin"),
    ("Año Nuevo", "01/01/2026"),
    ("Carnaval", "02/16/2026", "02/17/2026"),
    ("Viernes Santo", "04/03/2026"),
    ("Día del Trabajo", "05/01/2026"),
    ("Batalla de Pichincha", "05/24/2026"),
    ("Primer Grito de Independencia", "08/10/2026"),
    ("Independencia de Guayaquil", "10/09/2026"),
    ("Día de los Difuntos", "11/02/2026"),
    ("Independencia de Cuenca", "11/03/2026"),
    ("Navidad", "12/25/2026"),
]


def crear_excel_feriados(destino: Path) -> Path:
    destino.parent.mkdir(parents=True, exist_ok=True)
    libro = Workbook()
    hoja = libro.active
    hoja.title = "feriados"
    for fila in _FERIADOS_2026:
        hoja.append(fila)
    libro.save(destino)
    return destino


def main() -> int:
    settings = Settings()
    destino = settings.directorio_excel_feriados / settings.patron_excel_feriados
    ruta = crear_excel_feriados(destino)
    print(f"Plantilla feriados: {ruta.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
