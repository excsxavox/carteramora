from pathlib import Path
from typing import Optional

from sqlalchemy import event, text
from sqlalchemy.engine import Engine

from cobranzas.infrastructure.config.database_url import resolver_database_url
from cobranzas.infrastructure.config.settings import Settings
from cobranzas.infrastructure.persistence.base import Base
from cobranzas.infrastructure.persistence.session import get_engine


def _sqlite_path_from_url(database_url: str) -> Optional[Path]:
    if not database_url.startswith("sqlite"):
        return None
    raw = database_url.split("///", 1)[-1] if "///" in database_url else ""
    if not raw or raw == ":memory:":
        return None
    return Path(raw)


def prepare_database_url(database_url: str) -> str:
    """Crea carpeta del archivo SQLite si aplica."""
    path = _sqlite_path_from_url(database_url)
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
    return database_url


def create_engine_from_settings(settings: Settings) -> Engine:
    url = prepare_database_url(resolver_database_url(settings))
    engine = get_engine(url, echo=settings.db_echo)
    if engine.dialect.name == "sqlite":

        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def init_database(engine: Engine) -> None:
    """Crea tablas según modelos ORM (equivalente a Sql_BD_Cobranza para SQLite)."""
    import cobranzas.infrastructure.persistence.models  # noqa: F401
    import cobranzas.infrastructure.persistence.models.staging  # noqa: F401

    Base.metadata.create_all(bind=engine)


def verificar_conexion(engine: Engine) -> bool:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return True
