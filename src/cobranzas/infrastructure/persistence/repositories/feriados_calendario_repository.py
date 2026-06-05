from datetime import date
from typing import Set

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from cobranzas.domain.ports.feriados_calendario_port import FeriadosCalendarioPort
from cobranzas.domain.services.feriado_fechas import parsear_fecha_catalogo
from cobranzas.infrastructure.persistence.models import Catalogo, Clave


class SqlAlchemyFeriadosCalendarioRepository(FeriadosCalendarioPort):
    def __init__(self, session_factory: sessionmaker, clave_feriados: str) -> None:
        self._session_factory = session_factory
        self._clave_feriados = clave_feriados

    def fechas_vigentes(self) -> Set[date]:
        with self._session_factory() as session:
            id_clave = session.scalar(
                select(Clave.id_clave).where(Clave.clave == self._clave_feriados).limit(1)
            )
            if id_clave is None:
                return set()

            filas = session.scalars(
                select(Catalogo.valor).where(
                    Catalogo.id_clave == id_clave,
                    Catalogo.vigencia == True,  # noqa: E712 — SQL Server no acepta IS 1
                )
            ).all()

        fechas: Set[date] = set()
        for valor in filas:
            parsed = parsear_fecha_catalogo(valor)
            if parsed is not None:
                fechas.add(parsed)
        return fechas
