import logging
from pathlib import Path

from cobranzas.infrastructure.adapters.tab_lis_staging_reader import parsear_archivo_tab
from cobranzas.infrastructure.logging.archivo_lis_logger import ArchivoLisLogger


def test_archivo_lis_logger_no_requiere_tablas_bd(tmp_path: Path, caplog):
    caplog.set_level(logging.INFO, logger="cobranzas.archivo.lis")
    archivo = tmp_path / "detalle_morosidad.lis"
    archivo.write_text(
        "no_operacion\tsocio\tdias_atraso\n0015219214\t83736\t136\n",
        encoding="utf-8",
    )
    parseado = parsear_archivo_tab(archivo)
    ArchivoLisLogger(muestra_filas=1).log_archivo(archivo, parseado)

    texto = caplog.text
    assert "deudores" not in texto
    assert "asesores_deuda" not in texto
    assert "no_operacion" in texto
    assert "0015219214" in texto
    assert "dias_atraso" in texto
