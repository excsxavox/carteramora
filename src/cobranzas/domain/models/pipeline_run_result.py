from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PipelineRunResult:
    ok: bool
    codigo_salida: int
    fecha_corte: str
    archivo_morosidad: str
    archivo_cartera: str
    archivo_salida_morosidad: str
    archivo_salida_mora: str
    archivo_asignacion: str
    archivo_acumulado_mensual: Optional[str] = None
    total_en_mora: Optional[int] = None
    total_saldo_mora: Optional[float] = None
    registros_persistidos_bd: Optional[int] = None
    asignaciones_generadas: Optional[int] = None
    mensajes: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "codigo_salida": self.codigo_salida,
            "fecha_corte": self.fecha_corte,
            "archivos": {
                "entrada": {
                    "camorosico": self.archivo_morosidad,
                    "cadetacaco": self.archivo_cartera,
                },
                "salida": {
                    "detalle_morosidad": self.archivo_salida_morosidad,
                    "reporte_mora": self.archivo_salida_mora,
                    "asignacion_csv": self.archivo_asignacion,
                    "acumulado_mensual_xlsx": self.archivo_acumulado_mensual,
                },
            },
            "resumen": {
                "total_en_mora": self.total_en_mora,
                "total_saldo_mora": self.total_saldo_mora,
                "registros_persistidos_bd": self.registros_persistidos_bd,
                "asignaciones_generadas": self.asignaciones_generadas,
            },
            "mensajes": self.mensajes,
        }
