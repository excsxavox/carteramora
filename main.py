"""
Punto de entrada único — uso diario:

  python main.py

Ejecuta en orden (según .env):
  1. Preparar BD (tablas si no existen; migración: python main.py migrar-bd)
  2. Job 0  — Excel asesores → tabla asesores
  3. Job 0b — Excel feriados → catálogo (mora temprana)
  4. Job 1  — CAMOROSICO + CADETACACO → .lis, ASIGNACION.csv, BD
  5. Job 2  — staging tmp_* (solo si INCLUIR_STAGING_EN_PIPELINE=true)

Otros comandos: python main.py --help
"""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from cobranzas.jobs.cli import main

if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        sys.argv.append("pipeline")
    raise SystemExit(main())
