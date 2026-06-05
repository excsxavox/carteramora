from pathlib import Path
from typing import Optional

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from cobranzas.infrastructure.config.docsmora_resolver import resolver_rutas_cartera
from cobranzas.infrastructure.config.fecha_corte import parsear_fecha_corte


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
    db_trusted_connection: Optional[str] = Field(
        default=None,
        alias="DB_TRUSTED_CONNECTION",
        description="yes = autenticación integrada de Windows (ignora DB_USER/DB_PASSWORD)",
    )
    directorio_docsmora: Path = Field(
        default=Path("docsmora"),
        validation_alias=AliasChoices("DOCSMORA_DIR", "DIRECTORIO_DOCSMORA"),
    )
    directorio_destino: Path = Field(
        default=Path("destino"),
        validation_alias=AliasChoices("DESTINO_DIR", "DIRECTORIO_DESTINO"),
    )
    fecha_corte: Optional[str] = Field(
        default=None,
        alias="FECHA_CORTE",
        description="MMDDYYYY (mes-día-año); vacío = fecha de hoy",
    )
    usar_rutas_automaticas: bool = Field(
        default=True,
        alias="USAR_RUTAS_AUTOMATICAS",
        description="Busca .lis en docsmora/{año}/{hoy}/cartera{hoy}b",
    )
    archivo_morosidad: Optional[Path] = Field(
        default=None,
        alias="ARCHIVO_MOROSIDAD",
    )
    archivo_cartera: Optional[Path] = Field(
        default=None,
        alias="ARCHIVO_CARTERA",
    )
    archivo_salida_morosidad: Optional[Path] = Field(
        default=None,
        alias="ARCHIVO_SALIDA_MOROSIDAD",
    )
    archivo_salida_mora: Optional[Path] = Field(
        default=None,
        alias="ARCHIVO_SALIDA_MORA",
    )
    dias_mora_minimo: int = Field(default=30, alias="DIAS_MORA_MINIMO")
    usar_mora_temprana: bool = Field(default=True, alias="USAR_MORA_TEMPRANA")
    usar_reglas_bd: bool = Field(
        default=True,
        alias="USAR_REGLAS_BD",
        description="Si true, exclusiones y rango días desde tabla reglas",
    )
    mora_temprana_dias_min: int = Field(default=1, alias="MORA_TEMPRANA_DIAS_MIN")
    mora_temprana_dias_max: int = Field(default=1, alias="MORA_TEMPRANA_DIAS_MAX")
    estados_excluidos: str = Field(
        default="CASTIGADO,JUDICIAL,GESTION JUDICIAL",
        alias="ESTADOS_EXCLUIDOS",
    )
    tipos_oper_excluidos: str = Field(
        default="COMPRA CARTERA,COMPRACARTERA",
        alias="TIPOS_OPER_EXCLUIDOS",
    )
    archivo_salida_asignacion: Optional[Path] = Field(
        default=None,
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
    log_mora_muestra: int = Field(
        default=10,
        alias="LOG_MORA_MUESTRA",
        description=(
            "Operaciones de ejemplo en consola por motivo mora "
            "(-1=todas en INFO, 0=solo resumen, N=primeras N por categoría)"
        ),
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
    api_host: str = Field(default="127.0.0.1", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    deferir_resolucion_rutas: bool = Field(
        default=False,
        alias="DEFERIR_RESOLUCION_RUTAS",
        description="Si true, no valida carpetas .lis al cargar Settings (modo API)",
    )

    @model_validator(mode="after")
    def _aplicar_rutas_automaticas(self) -> "Settings":
        if not self.usar_rutas_automaticas:
            self._validar_rutas_manuales()
            return self

        if self.deferir_resolucion_rutas:
            return self

        if not self.fecha_corte:
            return self

        fecha = parsear_fecha_corte(self.fecha_corte)
        rutas = resolver_rutas_cartera(
            self.directorio_docsmora,
            self.directorio_destino,
            fecha=fecha,
        )

        if self.archivo_morosidad is None:
            self.archivo_morosidad = rutas.archivo_morosidad
        if self.archivo_cartera is None:
            self.archivo_cartera = rutas.archivo_cartera
        if self.archivo_salida_morosidad is None:
            self.archivo_salida_morosidad = rutas.archivo_salida_morosidad
        if self.archivo_salida_mora is None:
            self.archivo_salida_mora = rutas.archivo_salida_mora
        if self.archivo_salida_asignacion is None:
            self.archivo_salida_asignacion = rutas.archivo_salida_asignacion
        return self

    def _validar_rutas_manuales(self) -> None:
        faltantes = [
            nombre
            for nombre, valor in (
                ("ARCHIVO_MOROSIDAD", self.archivo_morosidad),
                ("ARCHIVO_CARTERA", self.archivo_cartera),
                ("ARCHIVO_SALIDA_MOROSIDAD", self.archivo_salida_morosidad),
                ("ARCHIVO_SALIDA_MORA", self.archivo_salida_mora),
                ("ARCHIVO_SALIDA_ASIGNACION", self.archivo_salida_asignacion),
            )
            if valor is None
        ]
        if faltantes:
            raise ValueError(
                "USAR_RUTAS_AUTOMATICAS=false requiere: " + ", ".join(faltantes)
            )
