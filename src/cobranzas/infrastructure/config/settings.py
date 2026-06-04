from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
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
    archivo_salida: Path = Field(
        default=Path("destino/2026/05042026/cartera05042026b/reporte_mora.json"),
        alias="ARCHIVO_SALIDA",
    )
    archivo_lis: Path = Field(
        default=Path("destino/2026/05042026/cartera05042026b/reporte_mora.lis"),
        alias="ARCHIVO_LIS",
    )
    dias_mora_minimo: int = Field(default=30, alias="DIAS_MORA_MINIMO")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
