"""Resultado de la conversión de archivos .lis a Excel."""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ArchivoConvertido:
    origen: str
    destino: str
    filas: int


@dataclass(frozen=True)
class LisExcelRunResult:
    ok: bool
    codigo_salida: int
    fecha: str
    archivos: Tuple[ArchivoConvertido, ...] = ()
    mensajes: Tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "codigo_salida": self.codigo_salida,
            "fecha": self.fecha,
            "archivos": [
                {"origen": a.origen, "destino": a.destino, "filas": a.filas}
                for a in self.archivos
            ],
            "mensajes": list(self.mensajes),
        }
