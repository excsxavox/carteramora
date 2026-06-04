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
    filas = [
        ("cedula", "nombre", "numero_telefono", "email", "activo"),
        ("087", "LADY JOHANNA GONZALEZ VELASQUEZ", "0990000001", "asesor1@cobranza.local", "si"),
        ("135", "ASESOR PRUEBA COBRANZAS", "0990000002", "asesor2@cobranza.local", "si"),
    ]
    for fila in filas:
        hoja.append(fila)
    libro.save(destino)

    print(f"Plantilla: {destino.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
