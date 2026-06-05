"""CLI unificada: python main.py [comando]"""

import argparse
import sys
from typing import Optional, Sequence


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Jobs de cartera en mora (hexagonal).",
    )
    sub = parser.add_subparsers(dest="comando")

    sub.add_parser(
        "pipeline",
        help="Job 0 + 0b + 1: asesores, feriados (Excel) y limpieza cartera",
    )
    sub.add_parser("sync", help="Job 0: Excel a tabla asesores")
    sub.add_parser("sync-feriados", help="Job 0b: Excel a catálogo de feriados")
    sub.add_parser(
        "sync-reglas",
        help="Sembrar tabla reglas (HU) desde .env si está vacía",
    )
    sub.add_parser("limpieza", help="Job 1: core .lis a destino .lis limpios")
    sub.add_parser("staging", help="Job 2: .lis limpios a tablas tmp_*")
    sub.add_parser("init-db", help="Crear tablas en DATABASE_URL")
    sub.add_parser(
        "plantilla",
        help="Generar data/catalogo/asesores.xlsx de ejemplo",
    )
    sub.add_parser(
        "plantilla-feriados",
        help="Generar data/catalogo/dias_feriados.xlsx (Ecuador)",
    )
    sub.add_parser(
        "migrar-bd",
        help="Añadir columnas nuevas deudor/deuda en SQLite existente",
    )
    sub.add_parser(
        "api",
        help="Servidor HTTP: POST /pipeline con body {\"fecha\": \"DDMMYYYY\"}",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    comando = args.comando or "pipeline"

    if comando == "pipeline":
        from cobranzas.jobs.pipeline_runner import main as run

        return run()
    if comando == "sync":
        from cobranzas.jobs.sync_asesores_runner import main as run

        return run()
    if comando == "sync-feriados":
        from cobranzas.jobs.sync_feriados_runner import main as run

        return run()
    if comando == "sync-reglas":
        from cobranzas.jobs.sync_reglas_runner import main as run

        return run()
    if comando == "limpieza":
        from cobranzas.jobs.runner import main as run

        return run()
    if comando == "staging":
        from cobranzas.jobs.cargar_staging_runner import main as run

        return run()
    if comando == "init-db":
        from cobranzas.jobs.init_db import main as run

        return run()
    if comando == "plantilla":
        from cobranzas.jobs.plantilla_asesores import main as run

        return run()
    if comando == "plantilla-feriados":
        from cobranzas.jobs.plantilla_feriados import main as run

        return run()
    if comando == "migrar-bd":
        from cobranzas.jobs.migrar_sqlite_schema import main as run

        return run()
    if comando == "api":
        from cobranzas.jobs.api_runner import main as run

        return run()

    _parser().print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
