from datetime import date
from pathlib import Path

import pytest

from cobranzas.infrastructure.config.docsmora_resolver import (
    carpeta_lote_docsmora,
    fecha_corte_ddmmyyyy,
    resolver_rutas_cartera,
)
from cobranzas.infrastructure.config.settings import Settings


def test_fecha_corte_ddmmyyyy():
    assert fecha_corte_ddmmyyyy(date(2026, 6, 5)) == "05062026"


def test_carpeta_lote_docsmora():
    ruta = carpeta_lote_docsmora(Path("docsmora"), "05062026")
    assert ruta.as_posix() == "docsmora/2026/05062026/cartera05062026b"


def test_resolver_encuentra_archivos_del_dia(tmp_path: Path):
    fecha = "05062026"
    lote = tmp_path / "docsmora" / "2026" / fecha / f"cartera{fecha}b"
    lote.mkdir(parents=True)
    mor = lote / f"camorosico_{fecha}_0047_of_0.lis"
    car = lote / f"cadetacaco_cie{fecha}_0233_of_0.lis"
    mor.write_text("x", encoding="utf-8")
    car.write_text("y", encoding="utf-8")

    rutas = resolver_rutas_cartera(
        tmp_path / "docsmora",
        tmp_path / "destino",
        fecha_ddmmyyyy=fecha,
    )
    assert rutas.archivo_morosidad == mor
    assert rutas.archivo_cartera == car
    assert rutas.archivo_salida_asignacion.parent == tmp_path / "destino" / "2026" / fecha / f"cartera{fecha}b"


def test_resolver_falla_si_no_hay_carpeta(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="carpeta de lote"):
        resolver_rutas_cartera(
            tmp_path / "docsmora",
            tmp_path / "destino",
            fecha_ddmmyyyy="05062026",
        )


def test_resolver_acepta_lis_con_fecha_distinta_en_nombre(tmp_path: Path):
    """El lote puede estar en carpeta 05042026 y el .lis traer 06032026 en el nombre."""
    fecha_carpeta = "05042026"
    lote = tmp_path / "docsmora" / "2026" / fecha_carpeta / f"cartera{fecha_carpeta}b"
    lote.mkdir(parents=True)
    mor = lote / "camorosico_06032026_0047_of_0.lis"
    car = lote / "cadetacaco_cie06032026_0233_of_0.lis"
    mor.write_text("x", encoding="utf-8")
    car.write_text("y", encoding="utf-8")

    rutas = resolver_rutas_cartera(
        tmp_path / "docsmora",
        tmp_path / "destino",
        fecha_ddmmyyyy=fecha_carpeta,
    )
    assert rutas.archivo_morosidad == mor
    assert rutas.archivo_cartera == car


def test_settings_resuelve_rutas_automaticas(tmp_path: Path, monkeypatch):
    fecha = "05042026"
    lote = tmp_path / "docsmora" / "2026" / fecha / f"cartera{fecha}b"
    lote.mkdir(parents=True)
    (lote / f"camorosico_{fecha}_0047_of_0.lis").write_text("m", encoding="utf-8")
    (lote / f"cadetacaco_cie{fecha}_0233_of_0.lis").write_text("c", encoding="utf-8")

    cfg = Settings(
        DOCSMORA_DIR=str(tmp_path / "docsmora"),
        DESTINO_DIR=str(tmp_path / "destino"),
        FECHA_CORTE=fecha,
        USAR_RUTAS_AUTOMATICAS=True,
    )
    assert cfg.archivo_morosidad.name.startswith("camorosico_")
    assert cfg.archivo_cartera.name.startswith("cadetacaco_")
