"""Filtros y cálculo de mora temprana (HU-GRC-01)."""

import logging
from dataclasses import replace
from datetime import date
from typing import List, Sequence, Set, Tuple

from cobranzas.domain.models.credito import Credito
from cobranzas.domain.services.dias_habiles_service import dias_mora_temprana
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
    ) -> Tuple[List[Credito], dict]:
        """
        Excluye operaciones no elegibles, recalcula días de mora y ordena por saldo DESC.
        """
        estados_excl = tuple(
            p.strip().upper() for p in estados_excluidos if p and str(p).strip()
        )
        tipos_excl = tuple(
            p.strip().upper() for p in tipos_oper_excluidos if p and str(p).strip()
        )

        elegibles: List[Credito] = []
        excluidos = 0
        sin_dia_pago = 0

        for credito in creditos:
            excluir, motivo = debe_excluir_operacion(
                credito, estados_excl, tipos_excl
            )
            if excluir:
                excluidos += 1
                logger.debug("Excluido %s: %s", credito.id_credito, motivo)
                continue

            dia_pago = dia_pago_desde_credito(credito)
            if usar_calculo_dia_pago and dia_pago > 0:
                dias = dias_mora_temprana(credito.fecha_corte, dia_pago, feriados)
            else:
                dias = credito.dias_mora

            if dia_pago <= 0 and usar_calculo_dia_pago:
                sin_dia_pago += 1

            if dias < dias_min or dias > dias_max:
                continue

            actualizado = replace(credito, dias_mora=dias)
            elegibles.append(actualizado)

        elegibles.sort(key=saldo_capital_desde_credito, reverse=True)

        metricas = {
            "total_entrada": len(creditos),
            "excluidos_regla": excluidos,
            "sin_dia_pago": sin_dia_pago,
            "en_mora_temprana": len(elegibles),
            "dias_min": dias_min,
            "dias_max": dias_max,
        }
        logger.info(
            "Mora temprana | entrada=%s excluidos=%s elegibles=%s (días %s-%s)",
            metricas["total_entrada"],
            excluidos,
            len(elegibles),
            dias_min,
            dias_max,
        )
        return elegibles, metricas
