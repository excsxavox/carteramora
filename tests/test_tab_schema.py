from cobranzas.domain.schemas.tab_schema import normalizar_encabezados


def test_normalizar_todas_las_columnas_morosidad():
    originales = (
        "MONEDA",
        "DES.OFICINA",
        "NO.OPERACION",
        "DIAS ATRASO",
        "CAP. MAS 180",
    )
    genericas = normalizar_encabezados(originales)
    assert genericas == (
        "moneda",
        "des_oficina",
        "no_operacion",
        "dias_atraso",
        "cap_mas_180",
    )


def test_encabezados_morosidad_fixture_tienen_todas_las_columnas_del_archivo():
    from pathlib import Path

    from cobranzas.infrastructure.adapters.cuadro_morosidad_parser import (
        leer_cuadro_morosidad,
    )

    fixture = Path(__file__).parent / "fixtures" / "cuadro_morosidad_consolidado.txt"
    _, columnas, creditos = leer_cuadro_morosidad(fixture)
    encabezado_archivo = (
        Path(__file__).parent / "fixtures" / "cuadro_morosidad_consolidado.txt"
    ).read_text(encoding="utf-8").splitlines()[2].split("\t")
    assert len(columnas) == len(encabezado_archivo)
    assert len(creditos[0].columnas_tab()) == len(encabezado_archivo)
