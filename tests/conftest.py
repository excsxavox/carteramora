"""Rutas de prueba cuando USAR_RUTAS_AUTOMATICAS=false."""

from pathlib import Path

import pytest

LOTE_FIXTURE = Path("docsmora/2026/05042026/cartera05042026b")

RUTAS_MANUALES_FIXTURE = {
    "USAR_RUTAS_AUTOMATICAS": "false",
    "ARCHIVO_MOROSIDAD": str(
        LOTE_FIXTURE / "camorosico_06032026_0047_of_0.lis"
    ),
    "ARCHIVO_CARTERA": str(
        LOTE_FIXTURE / "cadetacaco_cie06032026_0233_of_0.lis"
    ),
    "ARCHIVO_SALIDA_MOROSIDAD": str(
        Path("destino/2026/05042026/cartera05042026b/detalle_morosidad.lis")
    ),
    "ARCHIVO_SALIDA_MORA": str(
        Path("destino/2026/05042026/cartera05042026b/reporte_mora.lis")
    ),
    "ARCHIVO_SALIDA_ASIGNACION": str(
        Path("destino/2026/05042026/cartera05042026b/ASIGNACION.csv")
    ),
}


@pytest.fixture(autouse=True)
def _rutas_manuales_en_tests(monkeypatch):
    """Evita que pytest falle si no existe la carpeta del día en docsmora."""
    for clave, valor in RUTAS_MANUALES_FIXTURE.items():
        monkeypatch.setenv(clave, valor)
