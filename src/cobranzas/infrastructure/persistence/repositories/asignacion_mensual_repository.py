from typing import Dict, Tuple

from sqlalchemy import and_, extract, or_, select
from sqlalchemy.orm import sessionmaker

from cobranzas.domain.ports.asignacion_mensual_port import AsignacionMensualPort
from cobranzas.infrastructure.persistence.mappers.cobranza_credito_mapper import (
    ESTADO_ASESOR_MORA_TEMPRANA,
    codigo_usuario_desde_cedula_asesor,
)
from cobranzas.infrastructure.persistence.models import Asesor, AsesorDeuda, Deuda


class SqlAlchemyAsignacionMensualRepository(AsignacionMensualPort):
    def __init__(self, session_factory: sessionmaker) -> None:
        self._session_factory = session_factory

    def asignaciones_del_mes(self, anio: int, mes: int) -> Dict[str, Tuple[str, str]]:
        """
        Operaciones con asesor de mora temprana ya registradas en el mes.

        Usa la asignación más reciente por operación (fecha_asignacion desc).
        Incluye cortes del mes aunque fecha_asignacion no se haya actualizado aún.
        """
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
                    AsesorDeuda.id_asesor.isnot(None),
                    AsesorDeuda.estado == ESTADO_ASESOR_MORA_TEMPRANA,
                    or_(
                        and_(
                            extract("year", AsesorDeuda.fecha_asignacion) == anio,
                            extract("month", AsesorDeuda.fecha_asignacion) == mes,
                        ),
                        and_(
                            extract("year", Deuda.fecha_corte) == anio,
                            extract("month", Deuda.fecha_corte) == mes,
                        ),
                    ),
                )
                .order_by(
                    AsesorDeuda.fecha_asignacion.desc(),
                    AsesorDeuda.fecha_modificacion.desc(),
                )
            ).all()

        for numero_op, cedula, nombre in filas:
            clave = (numero_op or "").strip()
            if not clave or clave in resultado:
                continue
            codigo = codigo_usuario_desde_cedula_asesor(cedula or "")
            if not codigo:
                continue
            resultado[clave] = (codigo, (nombre or codigo).strip())
        return resultado
