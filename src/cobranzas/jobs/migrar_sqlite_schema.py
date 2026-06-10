"""Añade columnas nuevas a SQLite existente (deudores/deuda)."""

from cobranzas.infrastructure.config.settings import Settings
from cobranzas.infrastructure.persistence.database import create_engine_from_settings
from cobranzas.infrastructure.persistence.sqlite_schema_migrator import (
    migrar_sqlite_si_aplica,
)


def main() -> int:
    engine = create_engine_from_settings(Settings())
    if engine.dialect.name != "sqlite":
        print("Este script es solo para SQLite. Use Sql_BD_Cobranza_alter_deuda_deudor.sql")
        return 1

    aplicadas = migrar_sqlite_si_aplica(engine)
    print(f"Migración SQLite completada ({aplicadas} columna(s) nueva(s)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
