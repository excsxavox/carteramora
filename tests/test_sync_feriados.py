from datetime import date
from pathlib import Path

from openpyxl import Workbook

from cobranzas.domain.services.feriado_fechas import parsear_fecha_excel
from cobranzas.infrastructure.adapters.excel_feriado_reader import ExcelFeriadoReader
from cobranzas.infrastructure.config.settings import Settings
from cobranzas.infrastructure.persistence.database import (
    create_engine_from_settings,
    init_database,
)
from cobranzas.infrastructure.persistence.models import Catalogo, Clave
from cobranzas.infrastructure.persistence.repositories.feriado_catalogo_repository import (
    SqlAlchemyFeriadoCatalogoRepository,
)
from cobranzas.infrastructure.persistence.session import get_session_factory


def _crear_excel_feriados(path: Path, filas: list) -> None:
    libro = Workbook()
    hoja = libro.active
    for fila in filas:
        hoja.append(fila)
    libro.save(path)


def test_parsear_fecha_excel_mes_dia_anio():
    assert parsear_fecha_excel("12/25/2026") == date(2026, 12, 25)
    assert parsear_fecha_excel("01/01/2027") == date(2027, 1, 1)


def test_leer_feriado_un_dia(tmp_path: Path):
    archivo = tmp_path / "feriados_2026.xlsx"
    _crear_excel_feriados(
        archivo,
        [
            ("Navidad", "12/25/2026"),
        ],
    )
    reader = ExcelFeriadoReader()
    rangos = reader.leer_feriados(archivo)
    assert len(rangos) == 1
    assert rangos[0].descripcion == "Navidad"
    assert rangos[0].fecha_inicio == date(2026, 12, 25)
    assert rangos[0].fecha_fin == date(2026, 12, 25)


def test_sincronizar_feriado_inserta_catalogo(tmp_path: Path):
    archivo = tmp_path / "feriados_test.xlsx"
    _crear_excel_feriados(
        archivo,
        [
            ("Prueba feriado", "06/04/2026", "06/05/2026"),
        ],
    )
    db_path = tmp_path / "feriados.sqlite"
    engine = create_engine_from_settings(
        Settings(DATABASE_URL=f"sqlite:///{db_path.as_posix()}")
    )
    init_database(engine)
    repo = SqlAlchemyFeriadoCatalogoRepository(get_session_factory(engine))
    id_clave = repo.obtener_o_crear_clave("feriados_catalogo")
    detalle = repo.sincronizar_rango(
        id_clave,
        "Prueba feriado",
        date(2026, 6, 4),
        date(2026, 6, 5),
    )
    assert detalle.insertados == 2

    with get_session_factory(engine)() as session:
        clave = session.query(Clave).filter_by(clave="feriados_catalogo").one()
        filas = (
            session.query(Catalogo)
            .filter_by(id_clave=clave.id_clave, vigencia=True)
            .all()
        )
        valores = {f.valor for f in filas}
        assert valores == {"2026-06-04", "2026-06-05"}


def test_desactiva_dia_fuera_de_rango_excel(tmp_path: Path):
    db_path = tmp_path / "feriados2.sqlite"
    engine = create_engine_from_settings(
        Settings(DATABASE_URL=f"sqlite:///{db_path.as_posix()}")
    )
    init_database(engine)
    repo = SqlAlchemyFeriadoCatalogoRepository(get_session_factory(engine))
    id_clave = repo.obtener_o_crear_clave("feriados_catalogo")

    repo.sincronizar_rango(
        id_clave, "Navidad", date(2026, 12, 25), date(2027, 1, 1)
    )
    detalle = repo.sincronizar_rango(
        id_clave, "Navidad", date(2026, 12, 25), date(2026, 12, 31)
    )
    assert detalle.desactivados >= 1

    with get_session_factory(engine)() as session:
        inactivo = (
            session.query(Catalogo)
            .filter_by(valor="2027-01-01", vigencia=False)
            .one_or_none()
        )
        assert inactivo is not None
