from datetime import date
from pathlib import Path

from openpyxl import Workbook

from cobranzas.domain.models.credito import Credito
from cobranzas.infrastructure.adapters.recblue_archivo_adapter import RecblueArchivoAdapter
from cobranzas.infrastructure.config.settings import Settings
from cobranzas.infrastructure.persistence.database import (
    create_engine_from_settings,
    init_database,
)
from cobranzas.infrastructure.persistence.models import AsesorDeuda
from cobranzas.infrastructure.persistence.repositories.cobranza_repository import (
    SqlAlchemyCobranzaRepository,
)
from cobranzas.infrastructure.persistence.session import get_session_factory


def _crear_recblue_xlsx(path: Path) -> None:
    libro = Workbook()
    hoja = libro.active
    hoja.append(["ID Crédito", "Identificación Socio", "Número Operación"])
    hoja.append(["RB-1001", "1900299288", "0015219214"])
    libro.save(path)


def test_recblue_excel_valida_y_cruza_por_operacion(tmp_path: Path):
    archivo = tmp_path / "recblue.xlsx"
    _crear_recblue_xlsx(archivo)
    adapter = RecblueArchivoAdapter(archivo)
    mapa = adapter.id_credito_por_operacion()
    assert not adapter.errores_validacion
    assert mapa["0015219214"] == "RB-1001"


def test_persiste_id_credito_recblue_en_asesores_deuda(tmp_path: Path):
    recblue = tmp_path / "recblue.xlsx"
    _crear_recblue_xlsx(recblue)
    db_path = tmp_path / "rb.sqlite"
    engine = create_engine_from_settings(
        Settings(DATABASE_URL=f"sqlite:///{db_path.as_posix()}")
    )
    init_database(engine)
    factory = get_session_factory(engine)

    credito = Credito(
        "0015219214",
        "CLIENTE",
        500.0,
        5,
        date(2026, 3, 6),
        cedula="1900299288",
        codigo_oficial="520",
        nombre_oficial="ASESOR TEST",
        id_credito_recblue="RB-1001",
    )

    repo = SqlAlchemyCobranzaRepository(
        factory,
        dias_mora_minimo=1,
        recblue=RecblueArchivoAdapter(recblue),
    )
    assert repo.guardar_creditos_mora([credito]) == 1

    with factory() as session:
        fila = session.query(AsesorDeuda).one()
        assert fila.id_credito_recblue == "RB-1001"
