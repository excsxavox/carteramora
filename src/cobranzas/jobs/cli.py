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
        "plantilla-notificaciones",
        help="Generar data/catalogo/notificaciones_errores.xlsx",
    )
    sub.add_parser(
        "migrar-bd",
        help="Añadir columnas nuevas deudor/deuda en SQLite existente",
    )
    p_fin_mes = sub.add_parser(
        "fin-mes",
        help="Limpieza + merge (camorosico, cadetacaco, Recblue) → acumulado fin mes",
    )
    p_fin_mes.add_argument(
        "--fecha",
        help="Fecha del archivo MMDDYYYY o YYYY-MM-DD",
    )
    p_lis_excel = sub.add_parser(
        "lis-excel",
        help="Convierte camorosico + cadetacaco del lote a Excel (destino/excel_lis)",
    )
    p_lis_excel.add_argument(
        "--fecha",
        help="Fecha del archivo MMDDYYYY o YYYY-MM-DD",
    )
    sub.add_parser(
        "api",
        help="Servidor HTTP: POST /pipeline, /lis-a-excel y /acumulado-fin-mes",
    )
    p_seguir = sub.add_parser(
        "seguir-credito",
        help="Trazabilidad de un ID Recblue u operación core en el pipeline",
    )
    p_seguir.add_argument(
        "identificador",
        help="ID Crédito Recblue (ej. 27854) o número de operación",
    )
    p_seguir.add_argument(
        "--fecha",
        help="Fecha corte MMDDYYYY o YYYY-MM-DD",
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
    if comando == "plantilla-notificaciones":
        from cobranzas.jobs.plantilla_notificaciones import main as run

        return run()
    if comando == "migrar-bd":
        from cobranzas.jobs.migrar_sqlite_schema import main as run

        return run()
    if comando == "fin-mes":
        from cobranzas.jobs.fin_mes_runner import ejecutar_fin_mes

        return ejecutar_fin_mes(fecha_corte=args.fecha).codigo_salida
    if comando == "lis-excel":
        from cobranzas.jobs.lis_excel_runner import ejecutar_lis_a_excel

        return ejecutar_lis_a_excel(fecha=args.fecha).codigo_salida
    if comando == "api":
        from cobranzas.jobs.api_runner import main as run

        return run()
    if comando == "seguir-credito":
        from cobranzas.jobs.seguir_credito_runner import ejecutar_seguimiento

        return ejecutar_seguimiento(args.identificador, fecha=args.fecha)

    _parser().print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
