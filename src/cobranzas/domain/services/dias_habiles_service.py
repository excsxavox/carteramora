"""Cálculo de días hábiles y vencimiento efectivo (HU mora temprana)."""

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal, Optional, Set, Tuple

ClasificacionCuota = Literal["al_dia", "mora_temprana", "mora_madura"]


@dataclass(frozen=True)
class CuotaMoraCalculada:
    """Resultado del cálculo de mora según día de pago y mes de la cuota."""

    dias: int
    vencimiento_efectivo: date
    anio_cuota: int
    mes_cuota: int
    clasificacion: ClasificacionCuota


def es_fin_de_semana(fecha: date) -> bool:
    return fecha.weekday() >= 5


def es_feriado(fecha: date, feriados: Set[date]) -> bool:
    return fecha in feriados


def es_dia_habil(fecha: date, feriados: Set[date]) -> bool:
    return not es_fin_de_semana(fecha) and not es_feriado(fecha, feriados)


def siguiente_dia_habil(fecha: date, feriados: Set[date]) -> date:
    """Mueve la fecha al primer día hábil en o después de `fecha`."""
    actual = fecha
    while not es_dia_habil(actual, feriados):
        actual += timedelta(days=1)
    return actual


def fecha_pago_nominal(anio: int, mes: int, dia_pago: int) -> date:
    ultimo_dia = monthrange(anio, mes)[1]
    return date(anio, mes, min(dia_pago, ultimo_dia))


def vencimiento_efectivo(anio: int, mes: int, dia_pago: int, feriados: Set[date]) -> date:
    """Día hábil en que vence el pago del mes (sáb/dom/feriado → siguiente hábil)."""
    nominal = fecha_pago_nominal(anio, mes, dia_pago)
    return siguiente_dia_habil(nominal, feriados)


def _mes_anterior(anio: int, mes: int) -> Tuple[int, int]:
    if mes == 1:
        return anio - 1, 12
    return anio, mes - 1


def ultimo_vencimiento_hasta(
    fecha_corte: date, dia_pago: int, feriados: Set[date]
) -> date:
    """Último vencimiento efectivo de cuota en o antes de la fecha de corte."""
    venc, _, _ = ultimo_vencimiento_y_mes_pago(fecha_corte, dia_pago, feriados)
    return venc


def ultimo_vencimiento_y_mes_pago(
    fecha_corte: date, dia_pago: int, feriados: Set[date]
) -> Tuple[date, int, int]:
    """
    Último vencimiento efectivo <= corte y el mes/año de la cuota (mes de pago).
    """
    anio_prev, mes_prev = _mes_anterior(fecha_corte.year, fecha_corte.month)
    candidatos = (
        (fecha_corte.year, fecha_corte.month),
        (anio_prev, mes_prev),
    )
    mejor: Optional[Tuple[date, int, int]] = None
    for anio, mes in candidatos:
        venc = vencimiento_efectivo(anio, mes, dia_pago, feriados)
        if venc <= fecha_corte and (mejor is None or venc > mejor[0]):
            mejor = (venc, anio, mes)
    if mejor is not None:
        return mejor
    anio, mes = fecha_corte.year, fecha_corte.month
    return vencimiento_efectivo(anio, mes, dia_pago, feriados), anio, mes


def calcular_cuota_mora(
    fecha_corte: date, dia_pago: int, feriados: Set[date]
) -> CuotaMoraCalculada:
    """
    Calcula mora según HU:
    - Vencimiento hábil desde DIA PAGO (CADETACACO).
    - Mora inicia el día después del vencimiento hábil.
    - Mora temprana: cuota impaga del mes de la fecha de corte.
    - Mora madura: cuota impaga de un mes anterior.
    """
    if dia_pago <= 0:
        return CuotaMoraCalculada(
            dias=0,
            vencimiento_efectivo=fecha_corte,
            anio_cuota=fecha_corte.year,
            mes_cuota=fecha_corte.month,
            clasificacion="al_dia",
        )

    venc, anio_cuota, mes_cuota = ultimo_vencimiento_y_mes_pago(
        fecha_corte, dia_pago, feriados
    )
    es_mes_corte = (
        anio_cuota == fecha_corte.year and mes_cuota == fecha_corte.month
    )

    if fecha_corte <= venc:
        return CuotaMoraCalculada(
            dias=0,
            vencimiento_efectivo=venc,
            anio_cuota=anio_cuota,
            mes_cuota=mes_cuota,
            clasificacion="al_dia" if es_mes_corte else "mora_madura",
        )

    dias = (fecha_corte - venc).days
    if not es_mes_corte:
        return CuotaMoraCalculada(
            dias=dias,
            vencimiento_efectivo=venc,
            anio_cuota=anio_cuota,
            mes_cuota=mes_cuota,
            clasificacion="mora_madura",
        )

    return CuotaMoraCalculada(
        dias=dias,
        vencimiento_efectivo=venc,
        anio_cuota=anio_cuota,
        mes_cuota=mes_cuota,
        clasificacion="mora_temprana",
    )


def dias_mora_temprana(
    fecha_corte: date, dia_pago: int, feriados: Set[date]
) -> int:
    """
    Días de mora temprana (solo cuota del mes de la fecha de corte).
    Si la cuota impaga es de un mes anterior → 0 (mora madura).
    """
    resultado = calcular_cuota_mora(fecha_corte, dia_pago, feriados)
    if resultado.clasificacion != "mora_temprana":
        return 0
    return resultado.dias
