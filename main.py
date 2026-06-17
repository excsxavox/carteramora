"""
Punto de entrada único — uso diario:

  py -3 main.py

Ejecuta en orden (según .env):
  1. Preparar BD (tablas si no existen; migración: py -3 main.py migrar-bd)
  2. Job 0  — Excel asesores → tabla asesores
  3. Job 0b — Excel feriados → catálogo (mora temprana)
  4. Job 1  — CAMOROSICO + CADETACACO → .lis, ASIGNACION.csv, BD
  5. Job 2  — staging tmp_* (solo si INCLUIR_STAGING_EN_PIPELINE=true)

Otros comandos: py -3 main.py --help
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_SRC = _ROOT / "src"

if _SRC.is_dir():
    _src_str = str(_SRC)
    if _src_str not in sys.path:
        sys.path.insert(0, _src_str)

try:
    from cobranzas.jobs.cli import main
except ModuleNotFoundError as exc:
    if exc.name != "cobranzas":
        raise
    print(
        "No se encuentra el paquete 'cobranzas'.\n"
        f"  Carpeta del proyecto: {_ROOT}\n"
        f"  Se esperaba:          {_SRC / 'cobranzas'}\n"
        "\nSoluciones:\n"
        "  1) Copie este main.py actualizado (con bloque sys.path) al otro equipo/carpeta.\n"
        "  2) O instale el proyecto en el venv:\n"
        f"       cd \"{_ROOT}\"\n"
        '       pip install -e ".[api]"\n'
        "  3) O ejecute con PYTHONPATH:\n"
        f'       $env:PYTHONPATH="src"; py -3 main.py api\n',
        file=sys.stderr,
    )
    raise SystemExit(1) from exc

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("pipeline")
    raise SystemExit(main())
