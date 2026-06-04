"""
Punto de entrada único.

  python main.py              → pipeline (sync asesores + limpieza)
  python main.py sync         → solo Excel asesores
  python main.py limpieza     → solo limpieza cartera
  python main.py staging      → carga tablas temporales
  python main.py init-db      → crear BD
  python main.py plantilla    → crear Excel en data/catalogo/
  python main.py --help
"""

from cobranzas.jobs.cli import main

if __name__ == "__main__":
    import sys

    # Sin argumentos: pipeline (comportamiento por defecto)
    if len(sys.argv) == 1:
        sys.argv.append("pipeline")
    raise SystemExit(main())
