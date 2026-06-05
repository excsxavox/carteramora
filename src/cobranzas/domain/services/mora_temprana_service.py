"""Filtros y cálculo de mora temprana (HU-GRC-01)."""

import logging
from collections import defaultdict
from dataclasses import replace
from datetime import date
from typing import List, Optional, Sequence, Set, Tuple

from cobranzas.domain.models.credito import Credito
from cobranzas.domain.services.dias_habiles_service import (
    calcular_cuota_mora,
    parse_fecha_cadetacaco,
)

logger = logging.getLogger("cobranzas.mora_temprana")


def _parse_int_seguro(valor: str) -> int:
    try:
        return int(str(valor).strip().split(".")[0])
    except (ValueError, AttributeError):
        return 0


def saldo_capital_desde_credito(credito: Credito) -> float:
    for clave in ("saldo_cap_prest", "saldo_capital_prest", "saldo_capital_prestamo"):
        raw = credito.valor_campo(clave)
        if raw:
            try:
                return float(raw.replace(",", ""))
            except ValueError:
                continue
    return float(credito.saldo_pendiente or 0)


def dia_pago_desde_credito(credito: Credito) -> int:
    return _parse_int_seguro(credito.valor_campo("dia_pago"))


def fecha_ultimo_pago_desde_credito(credito: Credito) -> Optional[date]:
    """
    Último abono en CADETACACO (prioriza FECHA ULTIMO PAGO/ULTIMO ABONO).
    Solo fechas <= fecha de corte se usan en la regla de cuota impaga.
    """
    for clave in ("fecha_ultimo_pago_ultimo_abono", "fecha_ultimo_pago"):
        parsed = parse_fecha_cadetacaco(credito.valor_campo(clave))
        if parsed is not None:
            if parsed <= credito.fecha_corte:
                return parsed
    return None


def dias_atraso_camorosico(credito: Credito) -> int:
    """Referencia CAMOROSICO (columna S / DIAS ATRASO); no define la regla de días."""
    return int(credito.dias_mora or 0)


def _valores_estado(credito: Credito) -> Tuple[str, ...]:
    """CADETACACO (EST) tiene prioridad sobre CAMOROSICO (ESTADO)."""
    vistos: set[str] = set()
    ordenados: list[str] = []
    for raw in (
        credito.valor_campo("est"),
        credito.valor_campo("estado"),
        credito.estado_operacion,
    ):
        texto = (raw or "").strip().upper()
        if texto and texto not in vistos:
            vistos.add(texto)
            ordenados.append(texto)
    return tuple(ordenados)


def _valores_tipo_oper(credito: Credito) -> Tuple[str, ...]:
    """CADETACACO (TIPO OPER.) tiene prioridad sobre CAMOROSICO."""
    vistos: set[str] = set()
    ordenados: list[str] = []
    for raw in (credito.valor_campo("tipo_oper"), credito.tipo_operacion):
        texto = (raw or "").strip().upper()
        if texto and texto not in vistos:
            vistos.add(texto)
            ordenados.append(texto)
    return tuple(ordenados)


def debe_excluir_operacion(
    credito: Credito,
    estados_excluidos: Sequence[str],
    tipos_oper_excluidos: Sequence[str],
) -> Tuple[bool, str]:
    for estado in _valores_estado(credito):
        for patron in estados_excluidos:
            if patron and patron in estado:
                return True, f"estado={estado}"
    for tipo_oper in _valores_tipo_oper(credito):
        for patron in tipos_oper_excluidos:
            if patron and patron in tipo_oper:
                return True, f"tipo_oper={tipo_oper}"
    return False, ""


class MoraTempranaService:
    def procesar(
        self,
        creditos: List[Credito],
        feriados: Set[date],
        dias_min: int,
        dias_max: int,
        estados_excluidos: Sequence[str],
        tipos_oper_excluidos: Sequence[str],
        usar_calculo_dia_pago: bool = True,
        log_muestra: int = 10,
    ) -> Tuple[List[Credito], dict]:
        """
        Excluye operaciones no elegibles para mora temprana.

        - Días de mora: DIA PAGO + vencimiento hábil + conteo solo en días hábiles.
        - Cuota impaga: vencida al corte sin pago >= vencimiento (FECHA ULTIMO PAGO).
        - Elegible solo con exactamente 1 día hábil de mora (feriados/fines de semana).
        - CAMOROSICO (DIAS ATRASO) solo se registra como referencia en logs.
        """
        estados_excl = tuple(
            p.strip().upper() for p in estados_excluidos if p and str(p).strip()
        )
        tipos_excl = tuple(
            p.strip().upper() for p in tipos_oper_excluidos if p and str(p).strip()
        )

        elegibles: List[Credito] = []
        sin_dia_pago = 0
        contadores: dict[str, int] = defaultdict(int)
        muestras_info: dict[str, int] = defaultdict(int)

        def _log_decision(categoria: str, mensaje: str) -> None:
            contadores[categoria] += 1
            sin_limite = log_muestra < 0
            dentro_muestra = log_muestra > 0 and muestras_info[categoria] < log_muestra
            if sin_limite or dentro_muestra:
                logger.info(mensaje)
                if not sin_limite:
                    muestras_info[categoria] += 1
            else:
                logger.debug(mensaje)

        for credito in creditos:
            op = credito.id_credito
            excluir, motivo = debe_excluir_operacion(
                credito, estados_excl, tipos_excl
            )
            if excluir:
                _log_decision(
                    "excluido_regla",
                    f"Mora | op={op} | EXCLUIDO | {motivo}",
                )
                continue

            ref_camorosico = dias_atraso_camorosico(credito)
            dia_pago = dia_pago_desde_credito(credito)

            if not usar_calculo_dia_pago or dia_pago <= 0:
                sin_dia_pago += 1
                _log_decision(
                    "sin_dia_pago",
                    f"Mora | op={op} | NO_TEMPRANA | ref_camorosico={ref_camorosico} "
                    f"| motivo=sin_dia_pago",
                )
                continue

            ultimo_pago = fecha_ultimo_pago_desde_credito(credito)
            cuota = calcular_cuota_mora(
                credito.fecha_corte, dia_pago, feriados, ultimo_pago=ultimo_pago
            )
            dias = cuota.dias
            vencimiento = cuota.vencimiento_efectivo
            mes_cuota = f"{cuota.anio_cuota:04d}-{cuota.mes_cuota:02d}"
            ultimo_pago_str = ultimo_pago.isoformat() if ultimo_pago else "n/a"

            if cuota.clasificacion == "al_dia":
                _log_decision(
                    "cuota_al_dia",
                    f"Mora | op={op} | AL_DIA | ref_camorosico={ref_camorosico} "
                    f"| ultimo_pago={ultimo_pago_str} | dia_pago={dia_pago} "
                    f"| corte={credito.fecha_corte} | motivo=cuota_pagada_o_sin_venc",
                )
                continue

            base_detalle = (
                f"dias={dias} | origen=dia_pago | ref_camorosico={ref_camorosico} "
                f"| dia_pago={dia_pago} | ultimo_pago={ultimo_pago_str} "
                f"| mes_cuota={mes_cuota} | venc_efectivo={vencimiento} "
                f"| corte={credito.fecha_corte}"
            )

            if dias < dias_min:
                _log_decision(
                    "fuera_rango_bajo",
                    f"Mora | op={op} | FUERA_RANGO | {base_detalle} | motivo=dias<{dias_min}",
                )
                continue
            if dias > dias_max:
                _log_decision(
                    "fuera_rango_alto",
                    f"Mora | op={op} | FUERA_RANGO | {base_detalle} | motivo=dias>{dias_max}",
                )
                continue

            _log_decision(
                "elegible",
                f"Mora | op={op} | ELEGIBLE mora_temprana | {base_detalle}",
            )
            actualizado = replace(credito, dias_mora=dias)
            elegibles.append(actualizado)

        elegibles.sort(key=saldo_capital_desde_credito, reverse=True)

        excluidos = contadores["excluido_regla"]
        fuera_bajo = contadores["fuera_rango_bajo"]
        fuera_alto = contadores["fuera_rango_alto"]

        metricas = {
            "total_entrada": len(creditos),
            "excluidos_regla": excluidos,
            "mora_madura_mes_anterior": 0,
            "fuera_rango_bajo": fuera_bajo,
            "fuera_rango_alto": fuera_alto,
            "sin_dia_pago": sin_dia_pago,
            "en_mora_temprana": len(elegibles),
            "dias_min": dias_min,
            "dias_max": dias_max,
        }
        logger.info(
            "Mora resumen | entrada=%s | excluidos_regla=%s | "
            "fuera_rango (dias<%s)=%s | fuera_rango (dias>%s)=%s | "
            "sin_dia_pago=%s | al_dia=%s | elegibles=%s | dias_origen=dia_pago",
            metricas["total_entrada"],
            excluidos,
            dias_min,
            fuera_bajo,
            dias_max,
            fuera_alto,
            sin_dia_pago,
            contadores["cuota_al_dia"],
            len(elegibles),
        )
        if log_muestra == 0:
            logger.info(
                "Mora | detalle por operación en DEBUG (LOG_LEVEL=DEBUG) "
                "o active muestras con LOG_MORA_MUESTRA>0"
            )
        elif log_muestra > 0 and any(
            contadores[k] > muestras_info.get(k, 0) for k in contadores
        ):
            logger.info(
                "Mora | mostrando hasta %s ejemplos por categoría "
                "(LOG_MORA_MUESTRA=-1 para todas, LOG_LEVEL=DEBUG para el resto)",
                log_muestra,
            )
        return elegibles, metricas
