from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class FinMesRunResult:
    ok: bool
    codigo_salida: int
    fecha_archivo: str
    fecha_proceso: str
    archivo_morosidad: str
    archivo_cartera: str
    archivo_detalle_morosidad: str
    archivo_detalle_mora: str
    archivo_acumulado_fin_mes: Optional[str]
    total_en_mora: int
    total_saldo_mora: float
    filas_acumulado: int
    mensajes: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "codigo_salida": self.codigo_salida,
            "fecha_archivo": self.fecha_archivo,
            "fecha_proceso": self.fecha_proceso,
            "archivos": {
                "entrada": {
                    "camorosico": self.archivo_morosidad,
                    "cadetacaco": self.archivo_cartera,
                },
                "salida": {
                    "detalle_morosidad": self.archivo_detalle_morosidad,
                    "reporte_mora": self.archivo_detalle_mora,
                    "acumulado_fin_mes_xlsx": self.archivo_acumulado_fin_mes,
                },
            },
            "resumen": {
                "total_en_mora": self.total_en_mora,
                "total_saldo_mora": self.total_saldo_mora,
                "filas_acumulado": self.filas_acumulado,
            },
            "mensajes": list(self.mensajes),
        }
