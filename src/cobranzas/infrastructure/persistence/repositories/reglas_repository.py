from datetime import datetime
from typing import List

from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from cobranzas.domain.ports.reglas_repository_port import ReglaNegocio, ReglasRepositoryPort
from cobranzas.infrastructure.persistence.models import Regla


class SqlAlchemyReglasRepository(ReglasRepositoryPort):
    def __init__(self, session_factory: sessionmaker) -> None:
        self._session_factory = session_factory

    def contar_reglas(self) -> int:
        with self._session_factory() as session:
            return int(session.scalar(select(func.count()).select_from(Regla)) or 0)

    def listar_activas_por_tipos(self, tipos: frozenset[str]) -> List[ReglaNegocio]:
        if not tipos:
            return []
        with self._session_factory() as session:
            filas = session.scalars(
                select(Regla)
                .where(
                    Regla.activo.is_(True),
                    Regla.tipo.in_(tuple(tipos)),
                )
                .order_by(Regla.prioridad.desc(), Regla.id_regla)
            ).all()

        resultado: List[ReglaNegocio] = []
        for fila in filas:
            valor = (fila.valor or "").strip()
            tipo = (fila.tipo or "").strip()
            if not tipo or not valor:
                continue
            resultado.append(
                ReglaNegocio(
                    tipo=tipo,
                    valor=valor,
                    prioridad=int(fila.prioridad or 0),
                    nombre=fila.nombre,
                )
            )
        return resultado

    def insertar_reglas(self, reglas: List[ReglaNegocio]) -> int:
        if not reglas:
            return 0
        ahora = datetime.utcnow()
        with self._session_factory() as session:
            for regla in reglas:
                session.add(
                    Regla(
                        nombre=regla.nombre,
                        descripcion=regla.nombre,
                        tipo=regla.tipo,
                        valor=regla.valor,
                        prioridad=regla.prioridad,
                        activo=True,
                        creado_en=ahora,
                        fecha_modificacion=ahora,
                    )
                )
            session.commit()
        return len(reglas)
