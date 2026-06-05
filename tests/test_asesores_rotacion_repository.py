from pathlib import Path

from openpyxl import Workbook

from cobranzas.domain.services.sincronizar_asesores_service import (
    SincronizarAsesoresService,
)
from cobranzas.infrastructure.adapters.excel_asesor_reader import ExcelAsesorReader
from cobranzas.infrastructure.config.settings import Settings
from cobranzas.infrastructure.persistence.database import (
    create_engine_from_settings,
    init_database,
)
from cobranzas.infrastructure.persistence.repositories.asesor_sync_repository import (
    SqlAlchemyAsesorSyncRepository,
)
from cobranzas.infrastructure.persistence.repositories.asesores_rotacion_repository import (
    SqlAlchemyAsesoresRotacionRepository,
)
from cobranzas.infrastructure.persistence.session import get_session_factory


def test_listar_asesores_activos_desde_bd(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DB_SERVER", "")
    db_path = tmp_path / "asesores_rot.sqlite"
    engine = create_engine_from_settings(
        Settings(DATABASE_URL=f"sqlite:///{db_path.as_posix()}")
    )
    init_database(engine)
    factory = get_session_factory(engine)

    excel = tmp_path / "asesores.xlsx"
    libro = Workbook()
    hoja = libro.active
    hoja.append(["codigo_oficial", "nombre", "activo"])
    hoja.append(["LMANOSALVAS", "LUIS MANOSALVAS", "si"])
    hoja.append(["EGUERRA", "EDISON GUERRA", "si"])
    hoja.append(["INACTIVO", "NO USA", "no"])
    libro.save(excel)

    SincronizarAsesoresService(
        ExcelAsesorReader(),
        SqlAlchemyAsesorSyncRepository(factory),
    ).ejecutar(archivo_excel=excel)

    rotacion = SqlAlchemyAsesoresRotacionRepository(factory).listar_activos()
    assert rotacion == [
        ("LMANOSALVAS", "LUIS MANOSALVAS"),
        ("EGUERRA", "EDISON GUERRA"),
    ]
