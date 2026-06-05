import os

from cobranzas.infrastructure.config.database_url import (
    construir_url_sql_server,
    resolver_database_url,
)
from cobranzas.infrastructure.config.settings import Settings


def test_construir_url_sql_server_desde_db_vars():
    cfg = Settings(
        DB_SERVER="localhost",
        DB_DATABASE="BD_Cobranza",
        DB_USER="sa",
        DB_PASSWORD="pass@word",
        DB_DRIVER="ODBC Driver 18 for SQL Server",
        DB_TRUSTED_CONNECTION="no",
    )
    url = construir_url_sql_server(cfg)
    assert url.startswith("mssql+pyodbc://")
    assert "BD_Cobranza" in url
    assert "pass%40word" in url


def test_resolver_prioriza_database_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///tmp/test.sqlite")
    cfg = Settings(
        DATABASE_URL="sqlite:///tmp/test.sqlite",
        DB_SERVER="localhost",
        DB_DATABASE="BD_Cobranza",
    )
    assert resolver_database_url(cfg) == "sqlite:///tmp/test.sqlite"


def test_construir_url_sql_server_trusted_connection():
    cfg = Settings(
        DB_SERVER="localhost",
        DB_DATABASE="BD_Cobranza",
        DB_TRUSTED_CONNECTION="yes",
        DB_DRIVER="ODBC Driver 18 for SQL Server",
    )
    url = construir_url_sql_server(cfg)
    assert url.startswith("mssql+pyodbc://@")
    assert "trusted_connection=yes" in url
    assert "BD_Cobranza" in url


def test_resolver_usa_db_si_no_hay_database_url_en_entorno(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    cfg = Settings(
        DATABASE_URL="sqlite:///data/BD_Cobranza.sqlite",
        DB_SERVER="localhost",
        DB_DATABASE="BD_Cobranza",
        DB_USER="sa",
        DB_PASSWORD="x",
    )
    url = resolver_database_url(cfg)
    assert url.startswith("mssql+pyodbc://")
