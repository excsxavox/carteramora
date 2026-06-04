import json
from pathlib import Path

from cobranzas.infrastructure.config.settings import Settings
from cobranzas.infrastructure.persistence import Base
from cobranzas.infrastructure.persistence.database import (
    create_engine_from_settings,
    init_database,
)
from cobranzas.infrastructure.persistence.models.staging import (
    TmpColumnaArchivo,
    TmpLoteCarga,
    TmpStgMora,
    TmpStgMorosidad,
)
from cobranzas.infrastructure.persistence.repositories.staging_repository import (
    SqlAlchemyStagingRepository,
)
from cobranzas.infrastructure.persistence.session import get_session_factory
from cobranzas.infrastructure.adapters.tab_lis_staging_reader import parsear_archivo_tab


def _escribir_lis(path: Path, encabezado: str, filas: list[str]) -> None:
    path.write_text(
        encabezado + "\n" + "\n".join(filas) + "\n",
        encoding="utf-8",
    )


def test_parsear_archivo_tab_normaliza_encabezados(tmp_path: Path):
    archivo = tmp_path / "detalle.lis"
    _escribir_lis(
        archivo,
        "NO.OPERACION\tDIAS ATRASO",
        ["0012117441\t10", "0015219214\t136"],
    )
    parseado = parsear_archivo_tab(archivo)
    assert parseado.columnas == ("no_operacion", "dias_atraso")
    assert len(parseado.filas) == 2
    assert parseado.filas[0]["no_operacion"] == "0012117441"


def test_cargar_staging_crea_tablas_y_lote(tmp_path: Path):
    morosidad = tmp_path / "detalle_morosidad.lis"
    mora = tmp_path / "reporte_mora.lis"
    _escribir_lis(
        morosidad,
        "no_operacion\tsocio\tdias_atraso",
        ["0012117441\t80386\t10", "0015219214\t83736\t136"],
    )
    _escribir_lis(
        mora,
        "no_operacion\tcedula\tclasificacion_mora",
        ["0015219214\t1900299288\tmora_grave"],
    )

    db_path = tmp_path / "staging.sqlite"
    engine = create_engine_from_settings(
        Settings(DATABASE_URL=f"sqlite:///{db_path.as_posix()}")
    )
    init_database(engine)
    repo = SqlAlchemyStagingRepository(get_session_factory(engine))
    result = repo.cargar_archivos_limpios(morosidad, mora)

    assert result.id_lote == 1
    assert result.filas_morosidad == 2
    assert result.filas_mora == 1
    assert result.columnas_morosidad == 3
    assert result.columnas_mora == 3

    with get_session_factory(engine)() as session:
        lote = session.query(TmpLoteCarga).one()
        assert lote.filas_morosidad == 2
        assert lote.filas_mora == 1

        cols_mora = (
            session.query(TmpColumnaArchivo)
            .filter_by(id_lote=1, tipo_archivo="mora")
            .order_by(TmpColumnaArchivo.orden)
            .all()
        )
        assert [c.nombre_columna for c in cols_mora] == [
            "no_operacion",
            "cedula",
            "clasificacion_mora",
        ]

        fila = session.query(TmpStgMora).filter_by(no_operacion="0015219214").one()
        datos = json.loads(fila.campos_json)
        assert datos["cedula"] == "1900299288"
        assert datos["clasificacion_mora"] == "mora_grave"

        assert session.query(TmpStgMorosidad).count() == 2


def test_init_db_incluye_tablas_staging(tmp_path: Path):
    db_path = tmp_path / "all_tables.sqlite"
    engine = create_engine_from_settings(
        Settings(DATABASE_URL=f"sqlite:///{db_path.as_posix()}")
    )
    init_database(engine)
    nombres = {t.name for t in Base.metadata.sorted_tables}
    assert "tmp_lote_carga" in nombres
    assert "tmp_stg_morosidad" in nombres
    assert "tmp_stg_mora" in nombres
    assert "tmp_columna_archivo" in nombres
    assert "tmp_mapeo_columna" in nombres
