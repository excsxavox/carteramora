from pathlib import Path

from openpyxl import Workbook

from cobranzas.infrastructure.adapters.excel_asesor_reader import (
    ExcelAsesorReader,
    normalizar_cedula_asesor,
)
from cobranzas.infrastructure.config.settings import Settings
from cobranzas.infrastructure.persistence.database import (
    create_engine_from_settings,
    init_database,
)
from cobranzas.infrastructure.persistence.models import Asesor
from cobranzas.infrastructure.persistence.repositories.asesor_sync_repository import (
    SqlAlchemyAsesorSyncRepository,
)
from cobranzas.infrastructure.persistence.session import get_session_factory


def _crear_excel(path: Path, filas: list) -> None:
    libro = Workbook()
    hoja = libro.active
    for fila in filas:
        hoja.append(fila)
    libro.save(path)


def test_normalizar_cedula_oficial():
    assert normalizar_cedula_asesor("087") == "OF-87"
    assert normalizar_cedula_asesor("OF-135") == "OF-135"
    assert normalizar_cedula_asesor("LMANOSALVAS") == "OF-LMANOSALVAS"


def test_leer_excel_asesores(tmp_path: Path):
    archivo = tmp_path / "asesores.xlsx"
    _crear_excel(
        archivo,
        [
            ("codigo_oficial", "nombre", "telefono", "email", "activo"),
            ("520", "NATASHA ORCES", "0220000000", "n@test.com", "si"),
        ],
    )
    registros = ExcelAsesorReader().leer_asesores(archivo)
    assert len(registros) == 1
    assert registros[0].cedula == "OF-520"
    assert registros[0].nombre == "NATASHA ORCES"


def test_leer_excel_asesores_id_usuario_orden(tmp_path: Path):
    archivo = tmp_path / "asesores_usuario.xlsx"
    _crear_excel(
        archivo,
        [
            ("ID", "USUARIO", "ORDEN"),
            (2, "DARODRIGUEZ", 20),
            (1, "AMOLINA\xa0", 10),
        ],
    )
    registros = ExcelAsesorReader().leer_asesores(archivo)
    assert len(registros) == 2
    assert registros[0].cedula == "OF-AMOLINA"
    assert registros[0].nombre == "AMOLINA"
    assert registros[1].cedula == "OF-DARODRIGUEZ"
    assert registros[1].nombre == "DARODRIGUEZ"


def test_sincronizar_asesores_desde_excel(tmp_path: Path):
    archivo = tmp_path / "asesores.xlsx"
    _crear_excel(
        archivo,
        [
            ("cedula", "nombre", "activo"),
            ("OF-999", "ASESOR NUEVO EXCEL", "si"),
        ],
    )
    db_path = tmp_path / "sync.sqlite"
    engine = create_engine_from_settings(
        Settings(DATABASE_URL=f"sqlite:///{db_path.as_posix()}")
    )
    init_database(engine)
    registros = ExcelAsesorReader().leer_asesores(archivo)
    resultado = SqlAlchemyAsesorSyncRepository(get_session_factory(engine)).sincronizar(
        registros
    )
    assert resultado.creados == 1

    with get_session_factory(engine)() as session:
        asesor = session.query(Asesor).filter_by(cedula="OF-999").one()
        assert asesor.nombre == "ASESOR NUEVO EXCEL"
