from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from cobranzas.infrastructure.config.fecha_corte import normalizar_fecha_corte


class EjecutarPipelineRequest(BaseModel):
    fecha: str = Field(
        ...,
        description="Fecha de corte: MMDDYYYY (05052026) o YYYY-MM-DD (2026-05-05)",
        examples=["05052026", "2026-05-05"],
    )
    es_fin_de_mes: Optional[bool] = Field(
        default=None,
        description=(
            "Fin de mes: si es true, la mora temprana NO aplica tope máximo de días. "
            "Si se omite, usa el valor de .env (ES_FIN_DE_MES)."
        ),
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"fecha": "05052026", "es_fin_de_mes": False},
                {"fecha": "2026-05-05", "es_fin_de_mes": True},
            ]
        }
    }

    @field_validator("fecha")
    @classmethod
    def validar_fecha(cls, valor: str) -> str:
        return normalizar_fecha_corte(valor)


class ArchivosEntradaResponse(BaseModel):
    camorosico: str
    cadetacaco: str


class ArchivosSalidaResponse(BaseModel):
    detalle_morosidad: str
    reporte_mora: str
    asignacion_csv: str


class ArchivosResponse(BaseModel):
    entrada: ArchivosEntradaResponse
    salida: ArchivosSalidaResponse


class ResumenPipelineResponse(BaseModel):
    total_en_mora: Optional[int] = None
    total_saldo_mora: Optional[float] = None
    registros_persistidos_bd: Optional[int] = None
    asignaciones_generadas: Optional[int] = None


class FinMesRunResponse(BaseModel):
    ok: bool
    codigo_salida: int
    fecha_archivo: str
    fecha_proceso: str
    archivos: dict
    resumen: dict
    mensajes: List[str] = Field(default_factory=list)


class PipelineRunResponse(BaseModel):
    ok: bool
    codigo_salida: int
    fecha_corte: str
    archivos: ArchivosResponse
    resumen: ResumenPipelineResponse
    mensajes: List[str] = Field(default_factory=list)


class ArchivoConvertidoResponse(BaseModel):
    origen: str
    destino: str
    filas: int


class LisExcelRunResponse(BaseModel):
    ok: bool
    codigo_salida: int
    fecha: str
    archivos: List[ArchivoConvertidoResponse]
    mensajes: List[str] = Field(default_factory=list)
