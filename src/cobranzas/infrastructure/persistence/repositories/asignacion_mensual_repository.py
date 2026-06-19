from datetime import date
from typing import Dict, Optional, Tuple

from sqlalchemy import extract, select
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

    def asignaciones_del_mes(
        self, anio: int, mes: int, excluir_fecha: Optional[date] = None
    ) -> Dict[str, Tuple[str, str]]:
        """
        Operaciones ya asignadas a mora temprana en el mes calendario.

        Criterio: asesores_deuda con estado MORA_TEMPRANA y fecha_asignacion
        en (anio, mes). Día 2+ del mes solo rota las que no aparecen aquí.

        Si ``excluir_fecha`` se indica, se omiten las asignaciones de ese corte
        (al re-procesar un corte, su asignación previa no cuenta como conservada).
        """
        resultado: Dict[str, Tuple[str, str]] = {}
        condiciones = [
            Deuda.numero_operacion.isnot(None),
            AsesorDeuda.id_asesor.isnot(None),
            AsesorDeuda.estado == ESTADO_ASESOR_MORA_TEMPRANA,
            extract("year", AsesorDeuda.fecha_asignacion) == anio,
            extract("month", AsesorDeuda.fecha_asignacion) == mes,
        ]
        if excluir_fecha is not None:
            condiciones.append(AsesorDeuda.fecha_asignacion != excluir_fecha)
        with self._session_factory() as session:
            filas = session.execute(
                select(
                    Deuda.numero_operacion,
                    Asesor.cedula,
                    Asesor.nombre,
                )
                .join(AsesorDeuda, AsesorDeuda.id_deuda == Deuda.id_deuda)
                .join(Asesor, Asesor.id_asesor == AsesorDeuda.id_asesor)
                .where(*condiciones)
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
