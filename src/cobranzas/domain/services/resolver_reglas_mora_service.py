"""Resuelve parámetros de mora temprana desde tabla reglas (con fallback .env)."""

import logging
from typing import Optional, Sequence

from cobranzas.domain.constants.regla_tipo import (
    EXCLUSION_ESTADO,
    EXCLUSION_TIPO_OPER,
    MORA_TEMPRANA_DIAS_MAX,
    MORA_TEMPRANA_DIAS_MIN,
    TIPOS_MORA_TEMPRANA,
)
from cobranzas.domain.models.config_mora_temprana import ConfigMoraTemprana
from cobranzas.domain.ports.reglas_repository_port import ReglasRepositoryPort

logger = logging.getLogger("cobranzas.reglas")


class ResolverReglasMoraService:
    def __init__(
        self,
        repository: Optional[ReglasRepositoryPort] = None,
        usar_reglas_bd: bool = False,
    ) -> None:
        self._repo = repository
        self._usar_reglas_bd = usar_reglas_bd

    def resolver(
        self,
        dias_min: int,
        dias_max: int,
        estados_excluidos: Sequence[str],
        tipos_oper_excluidos: Sequence[str],
    ) -> ConfigMoraTemprana:
        fallback = ConfigMoraTemprana(
            dias_min=dias_min,
            dias_max=dias_max,
            estados_excluidos=tuple(
                p.strip().upper() for p in estados_excluidos if p and str(p).strip()
            ),
            tipos_oper_excluidos=tuple(
                p.strip().upper()
                for p in tipos_oper_excluidos
                if p and str(p).strip()
            ),
            origen="env",
        )
        if not self._usar_reglas_bd or self._repo is None:
            logger.info(
                "Reglas mora temprana desde .env | días %s-%s "
                "(max=0 calculado por cuota) | exclusiones estado=%s tipo_oper=%s",
                fallback.dias_min,
                fallback.dias_max,
                len(fallback.estados_excluidos),
                len(fallback.tipos_oper_excluidos),
            )
            return fallback

        reglas = self._repo.listar_activas_por_tipos(TIPOS_MORA_TEMPRANA)
        if not reglas:
            logger.info(
                "Reglas mora temprana desde .env (BD sin filas) | días %s-%s",
                fallback.dias_min,
                fallback.dias_max,
            )
            return fallback

        estados: list[str] = []
        tipos: list[str] = []
        min_dias: Optional[int] = None
        max_dias: Optional[int] = None

        for regla in reglas:
            valor = regla.valor.strip().upper()
            if regla.tipo == EXCLUSION_ESTADO:
                estados.append(valor)
            elif regla.tipo == EXCLUSION_TIPO_OPER:
                tipos.append(valor)
            elif regla.tipo == MORA_TEMPRANA_DIAS_MIN and min_dias is None:
                min_dias = _parse_int(regla.valor, dias_min)
            elif regla.tipo == MORA_TEMPRANA_DIAS_MAX and max_dias is None:
                max_dias = _parse_int(regla.valor, dias_max)

        config = ConfigMoraTemprana(
            dias_min=min_dias if min_dias is not None else dias_min,
            dias_max=max_dias if max_dias is not None else dias_max,
            estados_excluidos=tuple(estados) if estados else fallback.estados_excluidos,
            tipos_oper_excluidos=tuple(tipos)
            if tipos
            else fallback.tipos_oper_excluidos,
            origen="bd",
        )
        logger.info(
            "Reglas mora temprana desde BD | días %s-%s | exclusiones estado=%s tipo_oper=%s",
            config.dias_min,
            config.dias_max,
            len(config.estados_excluidos),
            len(config.tipos_oper_excluidos),
        )
        return config


def _parse_int(texto: str, default: int) -> int:
    try:
        return int(str(texto).strip())
    except (TypeError, ValueError):
        return default
