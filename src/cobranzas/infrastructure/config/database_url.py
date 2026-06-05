"""Resuelve DATABASE_URL desde .env (URL directa o variables DB_* de SQL Server)."""

import os
from urllib.parse import quote_plus

from cobranzas.infrastructure.config.settings import Settings


def construir_url_sql_server(settings: Settings) -> str:
    if not settings.db_server or not settings.db_database:
        raise ValueError("DB_SERVER y DB_DATABASE son obligatorios para SQL Server")

    driver = quote_plus(settings.db_driver or "ODBC Driver 18 for SQL Server")
    servidor = settings.db_server.strip()

    parametros = [f"driver={driver}"]
    if settings.db_encrypt:
        parametros.append(f"Encrypt={settings.db_encrypt}")
    if settings.db_trust_server_certificate:
        parametros.append(
            f"TrustServerCertificate={settings.db_trust_server_certificate}"
        )

    usa_windows = (settings.db_trusted_connection or "").strip().lower() in (
        "yes",
        "true",
        "1",
    )
    if usa_windows:
        parametros.append("trusted_connection=yes")
        query = "&".join(parametros)
        return f"mssql+pyodbc://@{servidor}/{settings.db_database}?{query}"

    usuario = quote_plus(settings.db_user or "")
    password = quote_plus(settings.db_password or "")
    query = "&".join(parametros)
    return f"mssql+pyodbc://{usuario}:{password}@{servidor}/{settings.db_database}?{query}"


def resolver_database_url(settings: Settings) -> str:
    """
    Prioridad:
    1. DATABASE_URL en .env
    2. DB_SERVER + DB_DATABASE + credenciales (como script feriados original)
    3. Valor por defecto de Settings (SQLite local)
    """
    if os.getenv("DATABASE_URL", "").strip():
        return settings.database_url.strip()

    if settings.db_server and settings.db_database:
        return construir_url_sql_server(settings)

    return settings.database_url
