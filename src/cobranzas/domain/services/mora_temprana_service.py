"""Filtros y clasificación de mora temprana (DIAS ATRASO de CAMOROSICO)."""

import logging
from collections import defaultdict
from datetime import date
from typing import List, Optional, Sequence, Set, Tuple

from cobranzas.domain.models.credito import Credito
from cobranzas.domain.services.dias_habiles_service import parse_fecha_cadetacaco

logger = logging.getLogger("cobranzas.mora_temprana")

# Regla mora temprana: días de atraso (CAMOROSICO) menores a 30 (1 a 29 inclusive).
PISO_DIAS_MORA_TEMPRANA_DEFAULT = 1
TOPE_DIAS_MORA_TEMPRANA_DEFAULT = 29


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


def fecha_ultimo_pago_desde_credito(
    credito: Credito,
    fecha_limite: Optional[date] = None,
) -> Optional[date]:
    """Último abono en CADETACACO (para detectar mora madura)."""
    limite = fecha_limite if fecha_limite is not None else credito.fecha_corte
    for clave in ("fecha_ultimo_pago_ultimo_abono", "fecha_ultimo_pago"):
        parsed = parse_fecha_cadetacaco(credito.valor_campo(clave))
        if parsed is not None and parsed <= limite:
            return parsed
    return None


def dias_atraso_camorosico(credito: Credito) -> int:
    """Días de atraso reportados en CAMOROSICO (columna DIAS ATRASO)."""
    return int(credito.dias_mora or 0)


def cuotas_atraso_camorosico(credito: Credito) -> int:
    """Cuotas atrasadas reportadas en CAMOROSICO (columna CUOTAS ATR.)."""
    return _parse_int_seguro(credito.valor_campo("cuotas_atr"))


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
    estados_permitidos: Sequence[str] = (),
) -> Tuple[bool, str]:
    estados = _valores_estado(credito)
    for estado in estados:
        for patron in estados_excluidos:
            if patron and patron in estado:
                return True, f"estado={estado}"
    if estados_permitidos:
        permitido = any(
            patron and patron in estado
            for estado in estados
            for patron in estados_permitidos
        )
        if not permitido:
            estado_txt = estados[0] if estados else "SIN_ESTADO"
            return True, f"estado_no_permitido={estado_txt}"
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
        dias_min: int = 0,
        dias_max: int = 0,
        estados_excluidos: Sequence[str] = (),
        tipos_oper_excluidos: Sequence[str] = (),
        log_muestra: int = 10,
        es_fin_de_mes: bool = False,
        estados_permitidos: Sequence[str] = (),
    ) -> Tuple[List[Credito], dict]:
        """
        Reglas (DIAS ATRASO de CAMOROSICO como único mandatario):

        - Lista base: operaciones en CAMOROSICO (DIAS ATRASO > 0).
        - Días de mora: el valor de DIAS ATRASO de CAMOROSICO, sin recálculo de
          días hábiles ni último pago.
        - MORA_TEMPRANA: DIAS ATRASO de CAMOROSICO menor a 30, es decir entre
          ``dias_min`` (default 1) y ``dias_max`` (default 29) días, inclusive.
        - MORA_MADURA: DIAS ATRASO fuera de ese rango (30 días o más).
        - ``es_fin_de_mes=True``: no se aplica tope máximo de días (se incluye
          toda operación con DIAS ATRASO >= ``dias_min``).
        - Exclusiones por estado/tipo de operación se mantienen.
        """
        piso_dias = (
            dias_min if dias_min and dias_min > 0 else PISO_DIAS_MORA_TEMPRANA_DEFAULT
        )
        tope_dias = (
            dias_max if dias_max and dias_max > 0 else TOPE_DIAS_MORA_TEMPRANA_DEFAULT
        )
        rango_txt = f"{piso_dias}-{'∞' if es_fin_de_mes else tope_dias}"
        estados_excl = tuple(
            p.strip().upper() for p in estados_excluidos if p and str(p).strip()
        )
        tipos_excl = tuple(
            p.strip().upper() for p in tipos_oper_excluidos if p and str(p).strip()
        )
        estados_perm = tuple(
            p.strip().upper() for p in estados_permitidos if p and str(p).strip()
        )

        elegibles: List[Credito] = []
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
                credito, estados_excl, tipos_excl, estados_perm
            )
            if excluir:
                _log_decision(
                    "excluido_regla",
                    f"Mora | op={op} | EXCLUIDO | {motivo}",
                )
                continue

            dias = dias_atraso_camorosico(credito)
            if dias <= 0:
                _log_decision(
                    "sin_dias_atraso",
                    f"Mora | op={op} | AL_DIA | dias_camorosico={dias} "
                    f"| motivo=sin_dias_atraso_camorosico",
                )
                continue

            fuera_piso = dias < piso_dias
            fuera_tope = (not es_fin_de_mes) and dias > tope_dias
            if fuera_piso or fuera_tope:
                _log_decision(
                    "fuera_rango_dias",
                    f"Mora | op={op} | MORA_MADURA | dias_camorosico={dias} "
                    f"| motivo=dias_fuera_de_rango_mora_temprana"
                    f"[{rango_txt}]",
                )
                continue

            _log_decision(
                "elegible",
                f"Mora | op={op} | ELEGIBLE mora_temprana | dias={dias} "
                f"| origen=camorosico | rango=[{rango_txt}] "
                f"| corte_archivo={credito.fecha_corte}",
            )
            elegibles.append(credito)

        elegibles.sort(key=saldo_capital_desde_credito, reverse=True)

        excluidos = contadores["excluido_regla"]

        metricas = {
            "total_entrada": len(creditos),
            "excluidos_regla": excluidos,
            "mora_madura": contadores["fuera_rango_dias"],
            "fuera_rango_dias": contadores["fuera_rango_dias"],
            "sin_dias_atraso": contadores["sin_dias_atraso"],
            "en_mora_temprana": len(elegibles),
            "dias_min": piso_dias,
            "dias_max": (0 if es_fin_de_mes else tope_dias),
            "es_fin_de_mes": es_fin_de_mes,
        }
        logger.info(
            "Mora resumen | entrada=%s | excluidos_regla=%s | "
            "sin_dias_atraso=%s | fuera_rango[%s-%s]=%s | "
            "elegibles=%s | dias_origen=camorosico | fin_de_mes=%s",
            metricas["total_entrada"],
            excluidos,
            contadores["sin_dias_atraso"],
            piso_dias,
            ("∞" if es_fin_de_mes else tope_dias),
            contadores["fuera_rango_dias"],
            len(elegibles),
            es_fin_de_mes,
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
