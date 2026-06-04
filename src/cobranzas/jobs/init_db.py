"""CLI: crea tablas BD_Cobranza en SQLite (o la URL configurada)."""

from cobranzas.infrastructure.config.settings import Settings
from cobranzas.infrastructure.persistence.database import (
    _sqlite_path_from_url,
    create_engine_from_settings,
    init_database,
    verificar_conexion,
)


def main() -> int:
    settings = Settings()
    engine = create_engine_from_settings(settings)
    init_database(engine)
    verificar_conexion(engine)

    path = _sqlite_path_from_url(settings.database_url)
    destino = path.resolve() if path else settings.database_url
    print(f"Base de datos lista: {destino}")
    print(f"URL: {settings.database_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
