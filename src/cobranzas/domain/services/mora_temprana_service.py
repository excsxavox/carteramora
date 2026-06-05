"""Filtros y cálculo de mora temprana (HU-GRC-01)."""

import logging
from collections import defaultdict
from dataclasses import replace
from datetime import date
from typing import List, Sequence, Set, Tuple

from cobranzas.domain.models.credito import Credito
from cobranzas.domain.services.dias_habiles_service import calcular_cuota_mora

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


def debe_excluir_operacion(
    credito: Credito,
    estados_excluidos: Sequence[str],
    tipos_oper_excluidos: Sequence[str],
) -> Tuple[bool, str]:
    estado = (
        credito.estado_operacion
        or credito.valor_campo("est")
        or credito.valor_campo("estado")
    ).upper()
    tipo_oper = (
        credito.tipo_operacion or credito.valor_campo("tipo_oper")
    ).upper()

    for patron in estados_excluidos:
        if patron and patron in estado:
            return True, f"estado={estado}"
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
        Excluye operaciones no elegibles, recalcula días de mora temprana
        (solo cuota del mes de corte) y ordena por saldo DESC.
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

            dia_pago = dia_pago_desde_credito(credito)
            mes_cuota = ""
            if usar_calculo_dia_pago and dia_pago > 0:
                cuota = calcular_cuota_mora(
                    credito.fecha_corte, dia_pago, feriados
                )
                dias = cuota.dias
                vencimiento = cuota.vencimiento_efectivo
                mes_cuota = f"{cuota.anio_cuota:04d}-{cuota.mes_cuota:02d}"
                origen_dias = "dia_pago"

                if cuota.clasificacion == "mora_madura":
                    _log_decision(
                        "mora_madura",
                        f"Mora | op={op} | MORA_MADURA | dias={dias} | mes_cuota={mes_cuota} "
                        f"| dia_pago={dia_pago} | venc_efectivo={vencimiento} "
                        f"| corte={credito.fecha_corte} | motivo=cuota_mes_anterior",
                    )
                    continue
            else:
                dias = credito.dias_mora
                vencimiento = None
                origen_dias = "camorosico"
                if usar_calculo_dia_pago:
                    sin_dia_pago += 1
                    _log_decision(
                        "sin_dia_pago_clasificar",
                        f"Mora | op={op} | NO_TEMPRANA | dias_camorosico={dias} "
                        f"| motivo=sin_dia_pago_para_mes_cuota",
                    )
                    continue

            venc_str = vencimiento.isoformat() if vencimiento else "n/a"
            base_detalle = (
                f"dias={dias} | origen={origen_dias} | dia_pago={dia_pago} "
                f"| mes_cuota={mes_cuota} | venc_efectivo={venc_str} "
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
        madura = contadores["mora_madura"]
        fuera_bajo = contadores["fuera_rango_bajo"]
        fuera_alto = contadores["fuera_rango_alto"]
        sin_dia_pago_clasificar = contadores["sin_dia_pago_clasificar"]

        metricas = {
            "total_entrada": len(creditos),
            "excluidos_regla": excluidos,
            "mora_madura_mes_anterior": madura,
            "fuera_rango_bajo": fuera_bajo,
            "fuera_rango_alto": fuera_alto,
            "sin_dia_pago": sin_dia_pago,
            "sin_dia_pago_clasificar": sin_dia_pago_clasificar,
            "en_mora_temprana": len(elegibles),
            "dias_min": dias_min,
            "dias_max": dias_max,
        }
        logger.info(
            "Mora resumen | entrada=%s | excluidos_regla=%s | mora_madura=%s | "
            "fuera_rango (dias<%s)=%s | fuera_rango (dias>%s)=%s | "
            "sin_dia_pago=%s | elegibles=%s",
            metricas["total_entrada"],
            excluidos,
            madura,
            dias_min,
            fuera_bajo,
            dias_max,
            fuera_alto,
            sin_dia_pago_clasificar,
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
