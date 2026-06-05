from datetime import date
from typing import Dict, Tuple

from sqlalchemy import extract, select
from sqlalchemy.orm import sessionmaker

from cobranzas.domain.ports.asignacion_mensual_port import AsignacionMensualPort
from cobranzas.infrastructure.persistence.mappers.cobranza_credito_mapper import (
    codigo_usuario_desde_cedula_asesor,
)
from cobranzas.infrastructure.persistence.models import Asesor, AsesorDeuda, Deuda


class SqlAlchemyAsignacionMensualRepository(AsignacionMensualPort):
    def __init__(self, session_factory: sessionmaker) -> None:
        self._session_factory = session_factory

    def asignaciones_del_mes(self, anio: int, mes: int) -> Dict[str, Tuple[str, str]]:
        resultado: Dict[str, Tuple[str, str]] = {}
        with self._session_factory() as session:
            filas = session.execute(
                select(
                    Deuda.numero_operacion,
                    Asesor.cedula,
                    Asesor.nombre,
                )
                .join(AsesorDeuda, AsesorDeuda.id_deuda == Deuda.id_deuda)
                .join(Asesor, Asesor.id_asesor == AsesorDeuda.id_asesor)
                .where(
                    Deuda.numero_operacion.isnot(None),
                    extract("year", AsesorDeuda.fecha_asignacion) == anio,
                    extract("month", AsesorDeuda.fecha_asignacion) == mes,
                )
            ).all()

        for numero_op, cedula, nombre in filas:
            if not numero_op:
                continue
            codigo = codigo_usuario_desde_cedula_asesor(cedula or "")
            resultado[str(numero_op)] = (codigo, (nombre or codigo).strip())
        return resultado
