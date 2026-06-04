"""Añade columnas nuevas a SQLite existente (deudores/deuda)."""

import sys

from sqlalchemy import text

from cobranzas.infrastructure.config.settings import Settings
from cobranzas.infrastructure.persistence.database import create_engine_from_settings

ALTERS = [
    "ALTER TABLE deudores ADD COLUMN socio VARCHAR(20)",
    "ALTER TABLE deuda ADD COLUMN oficina VARCHAR(20)",
    "ALTER TABLE deuda ADD COLUMN descripcion_oficina VARCHAR(100)",
    "ALTER TABLE deuda ADD COLUMN sector VARCHAR(10)",
    "ALTER TABLE deuda ADD COLUMN tipo_operacion VARCHAR(50)",
    "ALTER TABLE deuda ADD COLUMN tipo_destino VARCHAR(20)",
    "ALTER TABLE deuda ADD COLUMN valor_original_prestamo NUMERIC(18, 2)",
    "ALTER TABLE deuda ADD COLUMN saldo_capital_prestamo NUMERIC(18, 2)",
    "ALTER TABLE deuda ADD COLUMN calificacion VARCHAR(10)",
    "ALTER TABLE deuda ADD COLUMN total_provision NUMERIC(18, 2)",
    "ALTER TABLE deuda ADD COLUMN saldo NUMERIC(18, 2)",
]


def main() -> int:
    engine = create_engine_from_settings(Settings())
    if engine.dialect.name != "sqlite":
        print("Este script es solo para SQLite. Use Sql_BD_Cobranza_alter_deuda_deudor.sql")
        return 1

    with engine.begin() as conn:
        for sql in ALTERS:
            try:
                conn.execute(text(sql))
                print(f"OK: {sql}")
            except Exception as exc:
                if "duplicate column" in str(exc).lower():
                    print(f"Ya existe: {sql}")
                else:
                    raise
    print("Migración SQLite completada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
