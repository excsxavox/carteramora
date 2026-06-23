from datetime import date
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from cobranzas.domain.models.fila_acumulado_mensual import FilaAcumuladoMensual
from cobranzas.domain.ports.acumulado_mensual_port import AcumuladoMensualPort
from cobranzas.infrastructure.persistence.mappers.cobranza_credito_mapper import (
    ESTADO_ASESOR_FIN_DE_MES,
    ESTADO_ASESOR_MORA_TEMPRANA,
    codigo_usuario_desde_cedula_asesor,
)
from cobranzas.infrastructure.persistence.models import Asesor, AsesorDeuda, Deuda


class SqlAlchemyAcumuladoMensualRepository(AcumuladoMensualPort):
    def __init__(self, session_factory: sessionmaker) -> None:
        self._session_factory = session_factory

    def filas_por_fecha_corte(self, fecha_corte: date) -> List[FilaAcumuladoMensual]:
        with self._session_factory() as session:
            filas_db = session.execute(
                select(Deuda, AsesorDeuda, Asesor)
                .join(AsesorDeuda, AsesorDeuda.id_deuda == Deuda.id_deuda)
                .outerjoin(Asesor, Asesor.id_asesor == AsesorDeuda.id_asesor)
                .where(
                    Deuda.fecha_corte == fecha_corte,
                    AsesorDeuda.estado.in_(
                        (ESTADO_ASESOR_MORA_TEMPRANA, ESTADO_ASESOR_FIN_DE_MES)
                    ),
                )
                .order_by(Deuda.numero_operacion)
            ).all()

        resultado: List[FilaAcumuladoMensual] = []
        for deuda, asignacion, asesor in filas_db:
            usuario = (
                codigo_usuario_desde_cedula_asesor(asesor.cedula or "")
                if asesor is not None
                else ""
            )
            resultado.append(
                FilaAcumuladoMensual(
                    fecha_proceso=fecha_corte,
                    desc_oficina=(deuda.desc_oficina or deuda.oficina or "").strip(),
                    nombre=(deuda.nombre or "").strip(),
                    cedula=(deuda.cedula or "").strip(),
                    operacion=(deuda.numero_operacion or "").strip(),
                    tipo_oper=(deuda.tipo_operacion or "").strip(),
                    fecha_concesion=deuda.fecha_concesion,
                    valor_ori_prestamo=deuda.valor_original_prestamo,
                    saldo_cap_prest=deuda.saldo_capital_prestamo,
                    calificac=(deuda.calificacion or "").strip(),
                    total_provision=deuda.total_provision,
                    saldo_140x=deuda.saldo_140x,
                    saldo_141x=deuda.saldo_141x,
                    saldo_142x=deuda.saldo_142x,
                    total_op=deuda.total_operacion,
                    est=(deuda.estado or "").strip(),
                    estado_mora=(asignacion.estado or "").strip(),
                    dias_atraso_camorosico=deuda.dias_atraso_camorosico,
                    dias_mora=deuda.dias_mora,
                    tipo=(deuda.tipo or "").strip(),
                    dia_pago=deuda.dia_pago,
                    valor_cuota=deuda.valor_cuota,
                    cuota_act=deuda.cuota_actual,
                    dividendos=deuda.dividendos,
                    oficial_adm=(deuda.oficial_adm or "").strip(),
                    decision=(deuda.decision or "").strip(),
                    segmentacion=(deuda.segmentacion or "").strip(),
                    score=(deuda.score or "").strip(),
                    fuente_repago=(deuda.fuente_repago or "").strip(),
                    identificacion_ifi=(deuda.identificacion_ifi or "").strip(),
                    usuario_asesor=usuario,
                    nombre_asesor=(
                        (asesor.nombre or usuario).strip() if asesor is not None else ""
                    ),
                    id_credito_recblue=(asignacion.id_credito_recblue or "").strip(),
                )
            )
        return resultado
