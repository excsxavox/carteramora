"""Genera plantilla Excel en data/catalogo/notificaciones_errores.xlsx."""

from openpyxl import Workbook

from cobranzas.infrastructure.config.settings import Settings


def main() -> int:
    settings = Settings()
    destino = settings.archivo_excel_notificaciones
    destino.parent.mkdir(parents=True, exist_ok=True)

    libro = Workbook()
    hoja = libro.active
    hoja.title = "notificaciones"
    filas = [
        ("nombre", "email", "activo"),
        ("Soporte Cobranzas", "soporte.cobranzas@empresa.com", "si"),
        ("TI Operaciones", "ti.operaciones@empresa.com", "si"),
    ]
    for fila in filas:
        hoja.append(fila)
    libro.save(destino)

    print(f"Plantilla notificaciones: {destino.resolve()}")
    print("Edite los correos y active NOTIFICACIONES_ERRORES_HABILITADO=true en .env")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
