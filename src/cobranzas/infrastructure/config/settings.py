from pathlib import Path
from typing import Optional

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    archivo_excel_asesores: Path = Field(
        default=Path("data/catalogo/asesores.xlsx"),
        alias="ARCHIVO_EXCEL_ASESORES",
    )
    sync_asesores_rechazar_duplicados: bool = Field(
        default=True,
        alias="SYNC_ASESORES_RECHAZAR_DUPLICADOS",
        description="Si true, aborta si el Excel tiene la misma cédula en varias filas",
    )
    directorio_excel_feriados: Path = Field(
        default=Path("data/catalogo"),
        validation_alias=AliasChoices("EXCEL_DIR", "DIRECTORIO_EXCEL_FERIADOS"),
    )
    patron_excel_feriados: str = Field(
        default="dias_feriados.xlsx",
        validation_alias=AliasChoices("EXCEL_PATTERN", "PATRON_EXCEL_FERIADOS"),
    )
    clave_feriados: str = Field(
        default="feriados_catalogo",
        alias="CLAVE_FERIADOS",
    )
    log_dir: Path = Field(
        default=Path("logs"),
        validation_alias=AliasChoices("LOG_DIR", "LOG_DIR_FERIADOS"),
    )
    db_driver: Optional[str] = Field(
        default="ODBC Driver 18 for SQL Server",
        alias="DB_DRIVER",
    )
    db_server: Optional[str] = Field(default=None, alias="DB_SERVER")
    db_database: Optional[str] = Field(default=None, alias="DB_DATABASE")
    db_user: Optional[str] = Field(default=None, alias="DB_USER")
    db_password: Optional[str] = Field(default=None, alias="DB_PASSWORD")
    db_trust_server_certificate: Optional[str] = Field(
        default="yes",
        alias="DB_TRUST_SERVER_CERTIFICATE",
    )
    db_encrypt: Optional[str] = Field(default="yes", alias="DB_ENCRYPT")
    archivo_morosidad: Path = Field(
        default=Path(
            "docsmora/2026/05042026/cartera05042026b/camorosico_06032026_0047_of_0.lis"
        ),
        alias="ARCHIVO_MOROSIDAD",
    )
    archivo_cartera: Path = Field(
        default=Path(
            "docsmora/2026/05042026/cartera05042026b/cadetacaco_cie06032026_0233_of_0.lis"
        ),
        alias="ARCHIVO_CARTERA",
    )
    archivo_salida_morosidad: Path = Field(
        default=Path(
            "destino/2026/05042026/cartera05042026b/detalle_morosidad.lis"
        ),
        alias="ARCHIVO_SALIDA_MOROSIDAD",
    )
    archivo_salida_mora: Path = Field(
        default=Path("destino/2026/05042026/cartera05042026b/reporte_mora.lis"),
        alias="ARCHIVO_SALIDA_MORA",
    )
    dias_mora_minimo: int = Field(default=30, alias="DIAS_MORA_MINIMO")
    usar_mora_temprana: bool = Field(default=True, alias="USAR_MORA_TEMPRANA")
    mora_temprana_dias_min: int = Field(default=1, alias="MORA_TEMPRANA_DIAS_MIN")
    mora_temprana_dias_max: int = Field(default=29, alias="MORA_TEMPRANA_DIAS_MAX")
    estados_excluidos: str = Field(
        default="CASTIGADO,JUDICIAL,GESTION JUDICIAL",
        alias="ESTADOS_EXCLUIDOS",
    )
    tipos_oper_excluidos: str = Field(
        default="COMPRA CARTERA,COMPRACARTERA",
        alias="TIPOS_OPER_EXCLUIDOS",
    )
    asesores_rotacion: str = Field(
        default=(
            "AMOLINA,DARODRIGUEZ,KCANCHIG,GLOPEZ,FLLERENA,LMANOSALVAS,EGUERRA,MARCOS"
        ),
        alias="ASESORES_ROTACION",
    )
    archivo_salida_asignacion: Path = Field(
        default=Path("destino/2026/05042026/cartera05042026b/ASIGNACION.csv"),
        alias="ARCHIVO_SALIDA_ASIGNACION",
    )
    archivo_recblue: Optional[Path] = Field(
        default=None,
        alias="ARCHIVO_RECBLUE",
    )
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_muestra_mapeo: int = Field(
        default=0,
        alias="LOG_MUESTRA_MAPEO",
        description="Filas de ejemplo en logs .lis (0=desactivado)",
    )
    database_url: str = Field(
        default="sqlite:///data/BD_Cobranza.sqlite",
        alias="DATABASE_URL",
    )
    db_echo: bool = Field(default=False, alias="DB_ECHO")
    persistir_en_bd: bool = Field(default=True, alias="PERSISTIR_EN_BD")
    incluir_staging_en_pipeline: bool = Field(
        default=False,
        alias="INCLUIR_STAGING_EN_PIPELINE",
        description="Si true, python main.py también ejecuta Job 2 (tmp_*)",
    )
