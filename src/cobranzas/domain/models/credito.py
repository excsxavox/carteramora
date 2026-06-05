from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Sequence


class EstadoMora(str, Enum):
    AL_DIA = "al_dia"
    MORA_LEVE = "mora_leve"
    MORA_GRAVE = "mora_grave"


@dataclass(frozen=True)
class Credito:
    """Entidad unificada desde Cuadro de Morosidad y TE Detallado de Cartera."""

    id_credito: str
    cliente: str
    saldo_pendiente: float
    dias_mora: int
    fecha_corte: date
    estado_operacion: str = ""
    socio: str = ""
    oficina: str = ""
    nombre_oficial: str = ""
    tipo_operacion: str = ""
    total_atrasado: float = 0.0
    cedula: str = ""
    calificacion: str = ""
    total_operacion: float = 0.0
    segmentacion: str = ""
    fuente_repago: str = ""
    codigo_oficial: str = ""
    id_credito_recblue: str = ""
    campos_tab: tuple[tuple[str, str], ...] = ()

    def columnas_tab(self) -> tuple[str, ...]:
        return tuple(clave for clave, _ in self.campos_tab)

    def campos_tab_dict(self) -> dict[str, str]:
        return dict(self.campos_tab)

    def valor_campo(self, clave: str) -> str:
        return self.campos_tab_dict().get(clave, "").strip()

    def fila_tab(self, columnas: Sequence[str]) -> str:
        valores = self.campos_tab_dict()
        from cobranzas.domain.schemas.tab_schema import fila_tab

        return fila_tab(valores.get(columna, "") for columna in columnas)

    @staticmethod
    def combinar_campos_tab(
        base: tuple[tuple[str, str], ...],
        extra: tuple[tuple[str, str], ...],
    ) -> tuple[tuple[str, str], ...]:
        combinado = dict(base)
        for clave, valor in extra:
            if valor or clave not in combinado:
                combinado[clave] = valor
        return tuple(combinado.items())

    def clasificar_mora(self, dias_mora_minimo: int) -> EstadoMora:
        if self.dias_mora < dias_mora_minimo:
            return EstadoMora.AL_DIA
        if self.dias_mora < 90:
            return EstadoMora.MORA_LEVE
        return EstadoMora.MORA_GRAVE

    def esta_en_mora(self, dias_mora_minimo: int) -> bool:
        return self.clasificar_mora(dias_mora_minimo) != EstadoMora.AL_DIA
