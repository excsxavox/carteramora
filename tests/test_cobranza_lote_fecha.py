from datetime import date
from pathlib import Path

from cobranzas.domain.models.credito import Credito
from cobranzas.infrastructure.config.settings import Settings
from cobranzas.infrastructure.persistence.database import (
    create_engine_from_settings,
    init_database,
)
from cobranzas.infrastructure.persistence.models import AsesorDeuda, Deuda
from cobranzas.infrastructure.persistence.repositories.cobranza_repository import (
    SqlAlchemyCobranzaRepository,
)
from cobranzas.infrastructure.persistence.session import get_session_factory


def _credito(numero: str, fecha: date) -> Credito:
    return Credito(
        numero,
        f"Cliente {numero}",
        100.0,
        10,
        fecha,
        cedula=f"17{numero[-4:]}",
        codigo_oficial="520",
        nombre_oficial="ASESOR",
    )


def test_reemplaza_lote_misma_fecha_corte(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DB_SERVER", "")
    db_path = tmp_path / "lote.sqlite"
    engine = create_engine_from_settings(
        Settings(DATABASE_URL=f"sqlite:///{db_path.as_posix()}")
    )
    init_database(engine)
    repo = SqlAlchemyCobranzaRepository(get_session_factory(engine))
    fecha = date(2026, 6, 4)

    repo.guardar_creditos_mora([_credito("001", fecha), _credito("002", fecha)])

    with get_session_factory(engine)() as session:
        assert session.query(Deuda).filter_by(fecha_corte=fecha).count() == 2
        assert session.query(AsesorDeuda).count() == 2

    repo.guardar_creditos_mora([_credito("003", fecha)])

    with get_session_factory(engine)() as session:
        ops = {
            d.numero_operacion
            for d in session.query(Deuda).filter_by(fecha_corte=fecha).all()
        }
        assert ops == {"003"}
        assert session.query(AsesorDeuda).count() == 1


def test_rollback_si_falla_persistencia(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DB_SERVER", "")
    db_path = tmp_path / "rollback.sqlite"
    engine = create_engine_from_settings(
        Settings(DATABASE_URL=f"sqlite:///{db_path.as_posix()}")
    )
    init_database(engine)
    factory = get_session_factory(engine)
    repo = SqlAlchemyCobranzaRepository(factory)
    fecha = date(2026, 6, 4)

    original = repo._upsert_credito
    llamadas = {"n": 0}

    def _falla_en_segundo(session, credito):
        llamadas["n"] += 1
        if llamadas["n"] >= 2:
            raise RuntimeError("fallo simulado")
        return original(session, credito)

    monkeypatch.setattr(repo, "_upsert_credito", _falla_en_segundo)

    try:
        repo.guardar_creditos_mora([_credito("001", fecha), _credito("002", fecha)])
    except RuntimeError:
        pass

    with factory() as session:
        assert session.query(Deuda).filter_by(fecha_corte=fecha).count() == 0
        assert session.query(AsesorDeuda).count() == 0
