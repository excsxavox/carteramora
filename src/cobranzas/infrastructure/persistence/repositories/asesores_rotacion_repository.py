from typing import List, Tuple

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from cobranzas.domain.ports.asesores_rotacion_port import AsesoresRotacionPort
from cobranzas.infrastructure.persistence.mappers.cobranza_credito_mapper import (
    codigo_usuario_desde_cedula_asesor,
)
from cobranzas.infrastructure.persistence.models import Asesor


class SqlAlchemyAsesoresRotacionRepository(AsesoresRotacionPort):
    def __init__(self, session_factory: sessionmaker) -> None:
        self._session_factory = session_factory

    def listar_activos(self) -> List[Tuple[str, str]]:
        with self._session_factory() as session:
            filas = session.scalars(
                select(Asesor)
                .where(Asesor.activo == True)  # noqa: E712
                .order_by(Asesor.id_asesor)
            ).all()

        resultado: List[Tuple[str, str]] = []
        for asesor in filas:
            codigo = codigo_usuario_desde_cedula_asesor(asesor.cedula or "")
            if not codigo:
                continue
            nombre = (asesor.nombre or codigo).strip()
            resultado.append((codigo, nombre))
        return resultado
