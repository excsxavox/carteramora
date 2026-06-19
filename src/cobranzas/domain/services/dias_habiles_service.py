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
    cuotas_vencidas_impagas: int = 0


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


def fecha_consulta_mora(fecha_archivo: date, feriados: Set[date]) -> date:
    """
    Fecha efectiva para aplicar reglas de mora.

    El lote se nombra con la fecha del archivo, pero la consulta al core ocurre
    al día siguiente (día hábil). Ej.: archivo viernes 5-jun → consulta lunes 8-jun.
    """
    return siguiente_dia_habil(fecha_archivo + timedelta(days=1), feriados)


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
    """Fechas del core en CADETACACO (mm/dd/aaaa o dd/mm/aaaa)."""
    texto = (valor or "").strip()[:10]
    if not texto:
        return None
    for fmt in ("%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto, fmt).date()
        except ValueError:
            continue
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


def _sumar_meses(anio: int, mes: int, delta: int) -> Tuple[int, int]:
    indice = (anio * 12 + (mes - 1)) + delta
    return indice // 12, (indice % 12) + 1


def max_dias_mora_periodo_cuota(
    vencimiento: date,
    anio_cuota: int,
    mes_cuota: int,
    dia_pago: int,
    feriados: Set[date],
) -> int:
    """
    Tope de mora temprana mientras solo hay una cuota vencida impaga.

    El plazo llega hasta el vencimiento efectivo de la cuota siguiente (inclusive),
    día en que aún cuenta como una sola cuota estrictamente vencida.
    """
    anio_sig, mes_sig = _mes_siguiente(anio_cuota, mes_cuota)
    venc_siguiente = vencimiento_efectivo(anio_sig, mes_sig, dia_pago, feriados)
    if venc_siguiente <= vencimiento:
        return 0
    return contar_dias_mora_habiles(vencimiento, venc_siguiente, feriados)


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


def ultimo_pago_vigente_al_corte(
    ultimo_pago: Optional[date], fecha_corte: date
) -> Optional[date]:
    """Ignora abonos registrados después de la fecha de consulta."""
    if ultimo_pago is None or ultimo_pago > fecha_corte:
        return None
    return ultimo_pago


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
    pago = ultimo_pago_vigente_al_corte(ultimo_pago, fecha_corte)
    if pago is None:
        return False
    mes_consulta = (fecha_corte.year, fecha_corte.month)
    if (anio_cuota, mes_cuota) == mes_consulta:
        if pago.year != anio_cuota or pago.month != mes_cuota:
            return False
        return pago > vencimiento
    return pago >= vencimiento


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
    pago = ultimo_pago_vigente_al_corte(ultimo_pago, fecha_corte)
    anio = fecha_corte.year
    mes = fecha_corte.month
    venc = vencimiento_efectivo(anio, mes, dia_pago, feriados)
    if venc > fecha_corte:
        return None
    if cuota_consta_pagada(venc, pago, fecha_corte, anio, mes):
        return None
    return (venc, anio, mes)


def cuota_impaga_mes_anterior(
    fecha_corte: date,
    dia_pago: int,
    feriados: Set[date],
    ultimo_pago: Optional[date],
) -> Optional[Tuple[date, int, int]]:
    """
    Cuota impaga del mes calendario anterior al corte.

    Aplica cuando la cuota del mes de corte aún no venció pero el abono
    registrado no cubre el vencimiento del mes previo (ej. pago 21-abr y
    vencimiento 15-may impago al consultar 01-jun).
    """
    pago = ultimo_pago_vigente_al_corte(ultimo_pago, fecha_corte)
    if pago is None:
        return None
    anio_prev, mes_prev = _mes_anterior(fecha_corte.year, fecha_corte.month)
    venc = vencimiento_efectivo(anio_prev, mes_prev, dia_pago, feriados)
    if venc > fecha_corte:
        return None
    if cuota_consta_pagada(venc, pago, fecha_corte, anio_prev, mes_prev):
        return None
    return (venc, anio_prev, mes_prev)


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


def cuotas_vencidas_impagas(
    fecha_corte: date,
    dia_pago: int,
    feriados: Set[date],
    ultimo_pago: Optional[date] = None,
    max_meses: int = 120,
) -> Tuple[Tuple[date, int, int], ...]:
    """
    Cuotas impagas cuyo vencimiento efectivo es anterior al corte.

    Una cuota cuenta como vencida solo si ``vencimiento_efectivo < fecha_corte``
    (el día del vencimiento aún es día 0 y no suma como segunda cuota).
    """
    pago = ultimo_pago_vigente_al_corte(ultimo_pago, fecha_corte)
    impagas: list[Tuple[date, int, int]] = []
    anio, mes = fecha_corte.year, fecha_corte.month
    for _ in range(max_meses):
        venc = vencimiento_efectivo(anio, mes, dia_pago, feriados)
        if venc >= fecha_corte:
            anio, mes = _mes_anterior(anio, mes)
            continue
        if pago is None:
            impagas.append((venc, anio, mes))
            break
        if cuota_consta_pagada(venc, pago, fecha_corte, anio, mes):
            break
        impagas.append((venc, anio, mes))
        anio, mes = _mes_anterior(anio, mes)
    impagas.sort(key=lambda item: item[0])
    return tuple(impagas)


def _cuota_impaga_dia_vencimiento(
    fecha_corte: date,
    dia_pago: int,
    feriados: Set[date],
    ultimo_pago: Optional[date],
) -> Optional[Tuple[date, int, int]]:
    """Cuota impaga el mismo día de su vencimiento efectivo (día 0 de mora)."""
    pago = ultimo_pago_vigente_al_corte(ultimo_pago, fecha_corte)
    anio, mes = fecha_corte.year, fecha_corte.month
    venc = vencimiento_efectivo(anio, mes, dia_pago, feriados)
    if venc != fecha_corte:
        return None
    if cuota_consta_pagada(venc, pago, fecha_corte, anio, mes):
        return None
    return (venc, anio, mes)


def cuota_impaga_cruza_mes_consulta(
    anio_cuota: int, mes_cuota: int, fecha_consulta: date
) -> bool:
    """True si la cuota impaga pertenece a un mes anterior al de la consulta."""
    return (anio_cuota, mes_cuota) < (fecha_consulta.year, fecha_consulta.month)


def calcular_cuota_mora(
    fecha_corte: date,
    dia_pago: int,
    feriados: Set[date],
    ultimo_pago: Optional[date] = None,
) -> CuotaMoraCalculada:
    """
    Calcula mora según HU:
    - Vencimiento hábil desde DIA PAGO (sáb/dom/feriado → siguiente hábil).
    - 0 cuotas vencidas impagas → AL_DIA.
    - 1 cuota vencida impaga del mes de consulta → MORA_TEMPRANA.
    - 2+ cuotas vencidas impagas → MORA_MADURA.
    - 1 cuota impaga de mes anterior al de la consulta → MORA_MADURA (cruce de mes).
    - Días de mora: hábiles desde el día posterior al vencimiento de la cuota
      impaga más reciente (estrictamente vencida, o la del día 0 si aplica).
    """
    if dia_pago <= 0:
        return CuotaMoraCalculada(
            dias=0,
            vencimiento_efectivo=fecha_corte,
            anio_cuota=fecha_corte.year,
            mes_cuota=fecha_corte.month,
            clasificacion="al_dia",
            cuotas_vencidas_impagas=0,
        )

    impagas = cuotas_vencidas_impagas(
        fecha_corte, dia_pago, feriados, ultimo_pago=ultimo_pago
    )
    dia_cero = _cuota_impaga_dia_vencimiento(
        fecha_corte, dia_pago, feriados, ultimo_pago
    )
    cantidad = len(impagas)

    if cantidad == 0 and dia_cero is None:
        venc = vencimiento_efectivo(
            fecha_corte.year, fecha_corte.month, dia_pago, feriados
        )
        return CuotaMoraCalculada(
            dias=0,
            vencimiento_efectivo=venc,
            anio_cuota=fecha_corte.year,
            mes_cuota=fecha_corte.month,
            clasificacion="al_dia",
            cuotas_vencidas_impagas=0,
        )

    if cantidad >= 2:
        venc, anio_cuota, mes_cuota = impagas[-1]
        clasificacion: ClasificacionCuota = "mora_madura"
    elif cantidad == 1:
        venc, anio_cuota, mes_cuota = impagas[-1]
        clasificacion = "mora_temprana"
    else:
        venc, anio_cuota, mes_cuota = dia_cero
        clasificacion = "mora_temprana"

    if clasificacion == "mora_temprana" and cuota_impaga_cruza_mes_consulta(
        anio_cuota, mes_cuota, fecha_corte
    ):
        clasificacion = "mora_madura"

    dias = contar_dias_mora_habiles(venc, fecha_corte, feriados)
    return CuotaMoraCalculada(
        dias=dias,
        vencimiento_efectivo=venc,
        anio_cuota=anio_cuota,
        mes_cuota=mes_cuota,
        clasificacion=clasificacion,
        cuotas_vencidas_impagas=cantidad,
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


@dataclass(frozen=True)
class ClasificacionMoraCamorosico:
    """Clasificación de mora usando DIAS ATRASO de CAMOROSICO como mandatario."""

    clasificacion: ClasificacionCuota
    dias: int
    vencimiento_cuota: date
    limite_mes_siguiente: date
    anio_cuota: int
    mes_cuota: int


def clasificar_mora_camorosico(
    fecha_corte: date,
    dias_atraso: int,
    dia_pago: int,
    feriados: Set[date],
) -> ClasificacionMoraCamorosico:
    """
    Clasifica mora tomando los DIAS ATRASO de CAMOROSICO como valor mandatario.

    Reglas:
    - ``dias_atraso <= 0`` o sin ``dia_pago`` → AL_DIA (no entra a asignación).
    - MORA_TEMPRANA: una sola cuota vencida, es decir la fecha de corte aún NO
      alcanza el día de pago (ajustado a día hábil) del mes siguiente al de la
      cuota en mora.
    - MORA_MADURA: la fecha de corte ya alcanzó/pasó ese día límite del mes
      siguiente (habría 2 o más cuotas vencidas).

    No se recalculan los días de mora: ``dias`` siempre es el valor de CAMOROSICO.
    """
    if dias_atraso <= 0 or dia_pago <= 0:
        return ClasificacionMoraCamorosico(
            clasificacion="al_dia",
            dias=max(dias_atraso, 0),
            vencimiento_cuota=fecha_corte,
            limite_mes_siguiente=fecha_corte,
            anio_cuota=fecha_corte.year,
            mes_cuota=fecha_corte.month,
        )

    # La cuota en mora es la cuota cuyo vencimiento dio inicio al atraso.
    # Se estima por la fecha de inicio del atraso (corte - DIAS ATRASO) y se elige
    # el vencimiento (DIA PAGO ajustado a hábil) MÁS CERCANO a esa fecha, entre los
    # ya vencidos al corte. Tomar el "más cercano" evita errores de borde cuando los
    # DIAS ATRASO de CAMOROSICO no cuadran exactamente con el calendario.
    inicio_atraso = fecha_corte - timedelta(days=dias_atraso)
    candidatos = []
    for delta in (1, 0, -1):
        anio, mes = _sumar_meses(inicio_atraso.year, inicio_atraso.month, delta)
        venc = vencimiento_efectivo(anio, mes, dia_pago, feriados)
        if venc <= fecha_corte:
            candidatos.append((abs((venc - inicio_atraso).days), venc, anio, mes))

    if candidatos:
        candidatos.sort(key=lambda item: item[0])
        _, venc_cuota, anio_cuota, mes_cuota = candidatos[0]
    else:
        anio_cuota, mes_cuota = inicio_atraso.year, inicio_atraso.month
        venc_cuota = vencimiento_efectivo(anio_cuota, mes_cuota, dia_pago, feriados)

    anio_sig, mes_sig = _mes_siguiente(anio_cuota, mes_cuota)
    limite = vencimiento_efectivo(anio_sig, mes_sig, dia_pago, feriados)

    clasificacion: ClasificacionCuota = (
        "mora_temprana" if fecha_corte < limite else "mora_madura"
    )
    return ClasificacionMoraCamorosico(
        clasificacion=clasificacion,
        dias=dias_atraso,
        vencimiento_cuota=venc_cuota,
        limite_mes_siguiente=limite,
        anio_cuota=anio_cuota,
        mes_cuota=mes_cuota,
    )
