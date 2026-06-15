"""Genera plantilla Excel en data/catalogo/asesores.xlsx."""

from pathlib import Path

from openpyxl import Workbook

from cobranzas.infrastructure.config.settings import Settings


def main() -> int:
    settings = Settings()
    destino = settings.archivo_excel_asesores
    destino.parent.mkdir(parents=True, exist_ok=True)

    libro = Workbook()
    hoja = libro.active
    hoja.title = "asesores"
    # Orden de filas = orden de rotación (equivalente a columna ORDEN 10, 20, …).
    filas = [
        ("cedula", "nombre", "numero_telefono", "email", "activo"),
        ("AMOLINA", "AMOLINA", "", "", "si"),
        ("DARODRIGUEZ", "DARODRIGUEZ", "", "", "si"),
        ("KCANCHIG", "KCANCHIG", "", "", "si"),
        ("GLOPEZ", "GLOPEZ", "", "", "si"),
        ("FLLERENA", "FLLERENA", "", "", "si"),
        ("LMANOSALVAS", "LMANOSALVAS", "", "", "si"),
        ("EGUERRA", "EGUERRA", "", "", "si"),
        ("MARCOS", "MARCOS", "", "", "si"),
    ]
    for fila in filas:
        hoja.append(fila)
    libro.save(destino)

    print(f"Plantilla: {destino.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
