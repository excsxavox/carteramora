from pathlib import Path

from pydantic import Field
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
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_muestra_mapeo: int = Field(
        default=3,
        alias="LOG_MUESTRA_MAPEO",
        description="Cantidad de filas de ejemplo en logs de mapeo staging/persistencia",
    )
    database_url: str = Field(
        default="sqlite:///data/BD_Cobranza.sqlite",
        alias="DATABASE_URL",
    )
    db_echo: bool = Field(default=False, alias="DB_ECHO")
    persistir_en_bd: bool = Field(default=True, alias="PERSISTIR_EN_BD")
