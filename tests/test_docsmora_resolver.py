from datetime import date
from pathlib import Path

import pytest

from cobranzas.infrastructure.config.docsmora_resolver import (
    carpeta_lote_docsmora,
    resolver_rutas_cartera,
)
from cobranzas.infrastructure.config.fecha_corte import fecha_corte_mmddyyyy
from cobranzas.infrastructure.config.settings import Settings


def test_fecha_corte_mmddyyyy():
    assert fecha_corte_mmddyyyy(date(2026, 6, 5)) == "06052026"
    assert fecha_corte_mmddyyyy(date(2026, 5, 5)) == "05052026"


def test_carpeta_lote_docsmora():
    ruta = carpeta_lote_docsmora(Path("docsmora"), "05052026")
    assert ruta.as_posix() == "docsmora/2026/05052026/cartera05052026b"


def test_resolver_encuentra_archivos_del_dia(tmp_path: Path):
    fecha = "05052026"
    lote = tmp_path / "docsmora" / "2026" / fecha / f"cartera{fecha}b"
    lote.mkdir(parents=True)
    mor = lote / f"camorosico_{fecha}_0047_of_0.lis"
    car = lote / f"cadetacaco_cie{fecha}_0233_of_0.lis"
    mor.write_text("x", encoding="utf-8")
    car.write_text("y", encoding="utf-8")

    rutas = resolver_rutas_cartera(
        tmp_path / "docsmora",
        tmp_path / "destino",
        fecha_mmddyyyy=fecha,
    )
    assert rutas.archivo_morosidad == mor
    assert rutas.archivo_cartera == car
    assert rutas.archivo_salida_asignacion == (
        tmp_path / "destino" / "2026" / "05" / "ASIGNACION_05052026.csv"
    )


def test_resolver_falla_si_no_hay_carpeta(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="carpeta de lote"):
        resolver_rutas_cartera(
            tmp_path / "docsmora",
            tmp_path / "destino",
            fecha_mmddyyyy="06052026",
        )


def test_resolver_acepta_lis_con_fecha_distinta_en_nombre(tmp_path: Path):
    fecha_carpeta = "04052026"
    lote = tmp_path / "docsmora" / "2026" / fecha_carpeta / f"cartera{fecha_carpeta}b"
    lote.mkdir(parents=True)
    mor = lote / "camorosico_06032026_0047_of_0.lis"
    car = lote / "cadetacaco_cie06032026_0233_of_0.lis"
    mor.write_text("x", encoding="utf-8")
    car.write_text("y", encoding="utf-8")

    rutas = resolver_rutas_cartera(
        tmp_path / "docsmora",
        tmp_path / "destino",
        fecha_mmddyyyy=fecha_carpeta,
    )
    assert rutas.archivo_morosidad == mor
    assert rutas.archivo_cartera == car


def test_prioriza_cadetacaco_cie_sobre_cobra(tmp_path: Path):
    fecha = "05042026"
    lote = tmp_path / "docsmora" / "2026" / fecha / f"cartera{fecha}b"
    lote.mkdir(parents=True)
    mor = lote / f"camorosico_{fecha}_2327_of_0.lis"
    cie = lote / f"cadetacaco_cie{fecha}_0148_of_0.lis"
    cobra = lote / f"cadetacaco_cobra{fecha}_9999_of_0.lis"
    for archivo in (mor, cie, cobra):
        archivo.write_text("x", encoding="utf-8")

    rutas = resolver_rutas_cartera(
        tmp_path / "docsmora",
        tmp_path / "destino",
        fecha_mmddyyyy=fecha,
    )
    assert rutas.archivo_morosidad == mor
    assert rutas.archivo_cartera == cie


def test_cadetacaco_cobra_si_no_hay_cie(tmp_path: Path):
    fecha = "06052026"
    lote = tmp_path / "docsmora" / "2026" / fecha / f"cartera{fecha}b"
    lote.mkdir(parents=True)
    mor = lote / f"camorosico_{fecha}_2306_of_0.lis"
    cobra = lote / f"cadetacaco_cobra{fecha}_0136_of_0.lis"
    mor.write_text("x", encoding="utf-8")
    cobra.write_text("y", encoding="utf-8")

    rutas = resolver_rutas_cartera(
        tmp_path / "docsmora",
        tmp_path / "destino",
        fecha_mmddyyyy=fecha,
    )
    assert rutas.archivo_cartera == cobra


def test_settings_resuelve_rutas_automaticas(tmp_path: Path, monkeypatch):
    fecha = "04052026"
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

