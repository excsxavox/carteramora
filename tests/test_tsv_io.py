from datetime import date
from pathlib import Path

from cobranzas.domain.models.credito import Credito
from cobranzas.infrastructure.adapters.tsv_file_io import (
    TAB_DELIMITER,
    escribir_creditos_tsv,
    leer_creditos_tsv,
)


def test_leer_escribir_tsv_con_tabs(tmp_path: Path):
    archivo = tmp_path / "creditos.txt"
    credito = Credito("CR-1", "Cliente", 1000.5, 45, date(2026, 6, 1))
    escribir_creditos_tsv(archivo, [credito])

    contenido = archivo.read_text(encoding="utf-8")
    assert TAB_DELIMITER in contenido
    assert "," not in contenido.splitlines()[1]

    leidos = leer_creditos_tsv(archivo)
    assert len(leidos) == 1
    assert leidos[0].id_credito == "CR-1"
    assert leidos[0].dias_mora == 45
