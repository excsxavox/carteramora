"""Cálculo de días hábiles y vencimiento efectivo (HU mora temprana)."""

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, datetime, timedelta
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


def contar_dias_mora_habiles(
    vencimiento: date, fecha_corte: date, feriados: Set[date]
) -> int:
    """
    Días de mora contando solo días hábiles (lun–vie, sin feriados).

    La mora inicia el día posterior al vencimiento efectivo; sábados, domingos
    y feriados dentro del período no suman al conteo.
    """
    if fecha_corte <= vencimiento:
        return 0
    inicio = vencimiento + timedelta(days=1)
    cuenta = 0
    actual = inicio
    while actual <= fecha_corte:
        if es_dia_habil(actual, feriados):
            cuenta += 1
        actual += timedelta(days=1)
    return cuenta


def parse_fecha_cadetacaco(valor: str) -> Optional[date]:
    """Fechas del core en CADETACACO (dd/mm/aaaa)."""
    texto = (valor or "").strip()
    if not texto:
        return None
    try:
        return datetime.strptime(texto, "%d/%m/%Y").date()
    except ValueError:
        return None


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


def _mes_siguiente(anio: int, mes: int) -> Tuple[int, int]:
    if mes == 12:
        return anio + 1, 1
    return anio, mes + 1


def max_dias_mora_periodo_cuota(
    vencimiento: date,
    anio_cuota: int,
    mes_cuota: int,
    dia_pago: int,
    feriados: Set[date],
) -> int:
    """
    Máximo de días hábiles de mora temprana dentro del plazo de la cuota.

    El plazo va desde el día posterior al vencimiento efectivo de la cuota
    hasta el fin del mes calendario de la cuota (28/29/30/31 según mes) o el día
    anterior al siguiente vencimiento (lo que ocurra antes). Si la mora cruza al
    mes siguiente con la misma cuota, deja de ser temprana (mes_cuota vs mes_corte).
    """
    ultimo_dia_mes = date(
        anio_cuota, mes_cuota, monthrange(anio_cuota, mes_cuota)[1]
    )
    anio_sig, mes_sig = _mes_siguiente(anio_cuota, mes_cuota)
    venc_siguiente = vencimiento_efectivo(anio_sig, mes_sig, dia_pago, feriados)
    fin_plazo = min(ultimo_dia_mes, venc_siguiente - timedelta(days=1))
    if fin_plazo <= vencimiento:
        return 0
    return contar_dias_mora_habiles(vencimiento, fin_plazo, feriados)


def dias_max_mora_temprana_efectivo(
    vencimiento: date,
    anio_cuota: int,
    mes_cuota: int,
    dia_pago: int,
    feriados: Set[date],
    dias_max_config: int,
) -> int:
    """
    Tope de mora temprana para la cuota (días hábiles).

    Por defecto (dias_max_config <= 0) se calcula solo del período de la cuota
    (mes real + DIA PAGO). Un valor > 0 en config actúa como techo opcional.
    """
    tope_periodo = max_dias_mora_periodo_cuota(
        vencimiento, anio_cuota, mes_cuota, dia_pago, feriados
    )
    if dias_max_config <= 0:
        return tope_periodo
    return min(dias_max_config, tope_periodo)


def cuota_consta_pagada(
    vencimiento: date,
    ultimo_pago: Optional[date],
    fecha_corte: date,
    anio_cuota: int,
    mes_cuota: int,
) -> bool:
    """
    True si el último pago cubre la cuota evaluada al corte.

    - Mes de consulta (mes del corte): abono del mismo mes/año y con fecha
      estrictamente posterior al vencimiento (pago el mismo día del vencimiento
      no cancela mora al corte del día siguiente).
    - Meses anteriores: basta ultimo_pago >= vencimiento (abono tardío válido).
    """
    if ultimo_pago is None:
        return False
    if ultimo_pago > fecha_corte:
        return False
    mes_consulta = (fecha_corte.year, fecha_corte.month)
    if (anio_cuota, mes_cuota) == mes_consulta:
        if ultimo_pago.year != anio_cuota or ultimo_pago.month != mes_cuota:
            return False
        return ultimo_pago > vencimiento
    return ultimo_pago >= vencimiento


def cuota_impaga_al_corte(
    fecha_corte: date,
    dia_pago: int,
    feriados: Set[date],
    ultimo_pago: Optional[date],
) -> Optional[Tuple[date, int, int]]:
    """
    Cuota impaga del mes de consulta (mes calendario del corte).

    Mora temprana solo aplica a la cuota del período actual; meses anteriores
  ya cubiertos no se mezclan con el último pago del mes previo.
    """
    anio = fecha_corte.year
    mes = fecha_corte.month
    venc = vencimiento_efectivo(anio, mes, dia_pago, feriados)
    if venc > fecha_corte:
        return None
    if cuota_consta_pagada(venc, ultimo_pago, fecha_corte, anio, mes):
        return None
    return (venc, anio, mes)


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
    fecha_corte: date,
    dia_pago: int,
    feriados: Set[date],
    ultimo_pago: Optional[date] = None,
) -> CuotaMoraCalculada:
    """
    Calcula mora según HU:
    - Vencimiento hábil desde DIA PAGO (sáb/dom/feriado → siguiente hábil).
    - Cuota impaga: mes de consulta vencido sin pago del mismo mes calendario.
    - Días de mora: solo días hábiles desde el día posterior al vencimiento.
    - Mora temprana: solo cuota del mes del corte (no arrastra mes anterior).
    """
    if dia_pago <= 0:
        return CuotaMoraCalculada(
            dias=0,
            vencimiento_efectivo=fecha_corte,
            anio_cuota=fecha_corte.year,
            mes_cuota=fecha_corte.month,
            clasificacion="al_dia",
        )

    impaga = cuota_impaga_al_corte(fecha_corte, dia_pago, feriados, ultimo_pago)
    if impaga is None:
        venc, anio_cuota, mes_cuota = ultimo_vencimiento_y_mes_pago(
            fecha_corte, dia_pago, feriados
        )
        return CuotaMoraCalculada(
            dias=0,
            vencimiento_efectivo=venc,
            anio_cuota=anio_cuota,
            mes_cuota=mes_cuota,
            clasificacion="al_dia",
        )

    venc, anio_cuota, mes_cuota = impaga

    if fecha_corte <= venc:
        return CuotaMoraCalculada(
            dias=0,
            vencimiento_efectivo=venc,
            anio_cuota=anio_cuota,
            mes_cuota=mes_cuota,
            clasificacion="al_dia",
        )

    dias = contar_dias_mora_habiles(venc, fecha_corte, feriados)
    return CuotaMoraCalculada(
        dias=dias,
        vencimiento_efectivo=venc,
        anio_cuota=anio_cuota,
        mes_cuota=mes_cuota,
        clasificacion="mora_temprana" if dias > 0 else "al_dia",
    )


def dias_mora_temprana(
    fecha_corte: date,
    dia_pago: int,
    feriados: Set[date],
    ultimo_pago: Optional[date] = None,
) -> int:
    """
    Días de mora temprana si hay cuota impaga y días hábiles > 0.
    """
    resultado = calcular_cuota_mora(
        fecha_corte, dia_pago, feriados, ultimo_pago=ultimo_pago
    )
    if resultado.clasificacion != "mora_temprana":
        return 0
    return resultado.dias
