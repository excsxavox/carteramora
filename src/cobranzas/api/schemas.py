from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from cobranzas.infrastructure.config.fecha_corte import normalizar_fecha_corte


class EjecutarPipelineRequest(BaseModel):
    fecha: str = Field(
        ...,
        description="Fecha de corte: DDMMYYYY (05042026) o YYYY-MM-DD (2026-04-05)",
        examples=["05042026", "2026-04-05"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"fecha": "05042026"},
                {"fecha": "2026-04-05"},
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


class PipelineRunResponse(BaseModel):
    ok: bool
    codigo_salida: int
    fecha_corte: str
    archivos: ArchivosResponse
    resumen: ResumenPipelineResponse
    mensajes: List[str] = Field(default_factory=list)
