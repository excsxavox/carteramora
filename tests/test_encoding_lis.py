from pathlib import Path

from cobranzas.infrastructure.adapters.parser_comun import leer_lineas_archivo


def test_leer_cp1252_con_enie(tmp_path: Path):
    archivo = tmp_path / "mora.lis"
    archivo.write_bytes(
        "CUADRO DE MOROSIDAD - CONSOLIDADO\n"
        "CORTE A: 06/03/2026\n"
        "ESPINOSA\n".encode("cp1252")
    )
    lineas = leer_lineas_archivo(archivo)
    assert "CUADRO DE MOROSIDAD" in lineas[0]
    assert "ESPINOSA" in lineas[2] or "ESPA" in lineas[2]
