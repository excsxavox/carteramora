"""Carga reglas HU-GRC-01 en tabla reglas si está vacía."""

import logging
from typing import Sequence, Tuple

from cobranzas.domain.constants.regla_tipo import (
    EXCLUSION_ESTADO,
    EXCLUSION_TIPO_OPER,
    MORA_TEMPRANA_DIAS_MAX,
    MORA_TEMPRANA_DIAS_MIN,
)
from cobranzas.domain.ports.reglas_repository_port import ReglaNegocio, ReglasRepositoryPort

logger = logging.getLogger("cobranzas.reglas")

_REGULAS_INICIALES: Tuple[ReglaNegocio, ...] = (
    ReglaNegocio(
        nombre="Excluir castigado (CADETACACO est → deuda.estado)",
        tipo=EXCLUSION_ESTADO,
        valor="CASTIGADO",
        prioridad=10,
    ),
    ReglaNegocio(
        nombre="Excluir judicial",
        tipo=EXCLUSION_ESTADO,
        valor="JUDICIAL",
        prioridad=20,
    ),
    ReglaNegocio(
        nombre="Excluir gestión judicial",
        tipo=EXCLUSION_ESTADO,
        valor="GESTION JUDICIAL",
        prioridad=30,
    ),
    ReglaNegocio(
        nombre="Excluir compra de cartera",
        tipo=EXCLUSION_TIPO_OPER,
        valor="COMPRA CARTERA",
        prioridad=10,
    ),
    ReglaNegocio(
        nombre="Excluir compracartera",
        tipo=EXCLUSION_TIPO_OPER,
        valor="COMPRACARTERA",
        prioridad=20,
    ),
    ReglaNegocio(
        nombre="Mora temprana días mínimo",
        tipo=MORA_TEMPRANA_DIAS_MIN,
        valor="1",
        prioridad=0,
    ),
    ReglaNegocio(
        nombre="Mora temprana días máximo",
        tipo=MORA_TEMPRANA_DIAS_MAX,
        valor="29",
        prioridad=0,
    ),
)


def reglas_iniciales_desde_env(
    estados_excluidos: Sequence[str],
    tipos_oper_excluidos: Sequence[str],
    dias_min: int,
    dias_max: int,
) -> Tuple[ReglaNegocio, ...]:
    """Construye semilla desde .env (prioridad sobre valores fijos si se personaliza)."""
    estados = [p.strip().upper() for p in estados_excluidos if p and str(p).strip()]
    tipos = [p.strip().upper() for p in tipos_oper_excluidos if p and str(p).strip()]
    if not estados and not tipos:
        return _REGULAS_INICIALES

    reglas: list[ReglaNegocio] = []
    for i, patron in enumerate(estados):
        reglas.append(
            ReglaNegocio(
                nombre=f"Excluir estado {patron}",
                tipo=EXCLUSION_ESTADO,
                valor=patron,
                prioridad=100 - i,
            )
        )
    for i, patron in enumerate(tipos):
        reglas.append(
            ReglaNegocio(
                nombre=f"Excluir tipo oper {patron}",
                tipo=EXCLUSION_TIPO_OPER,
                valor=patron,
                prioridad=100 - i,
            )
        )
    reglas.append(
        ReglaNegocio(
            nombre="Mora temprana días mínimo",
            tipo=MORA_TEMPRANA_DIAS_MIN,
            valor=str(dias_min),
            prioridad=0,
        )
    )
    reglas.append(
        ReglaNegocio(
            nombre="Mora temprana días máximo",
            tipo=MORA_TEMPRANA_DIAS_MAX,
            valor=str(dias_max),
            prioridad=0,
        )
    )
    return tuple(reglas)


class SembrarReglasMoraService:
    def __init__(self, repository: ReglasRepositoryPort) -> None:
        self._repo = repository

    def sembrar_si_vacio(
        self,
        estados_excluidos: Sequence[str] = (),
        tipos_oper_excluidos: Sequence[str] = (),
        dias_min: int = 1,
        dias_max: int = 29,
    ) -> int:
        if self._repo.contar_reglas() > 0:
            return 0
        reglas = reglas_iniciales_desde_env(
            estados_excluidos, tipos_oper_excluidos, dias_min, dias_max
        )
        insertadas = self._repo.insertar_reglas(list(reglas))
        logger.info("Reglas HU sembradas en BD: %s filas", insertadas)
        return insertadas
