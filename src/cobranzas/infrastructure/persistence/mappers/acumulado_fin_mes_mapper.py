"""Credito en mora → fila del Excel acumulado fin de mes (deudores + deuda)."""

from datetime import date
from typing import Optional

from cobranzas.domain.models.credito import Credito
from cobranzas.domain.models.fila_acumulado_fin_mes import FilaAcumuladoFinMes
from cobranzas.domain.services.feriado_fechas import parsear_fecha_catalogo
from cobranzas.infrastructure.persistence.mappers.cobranza_credito_mapper import (
    clasificacion_mora_valor,
)
from cobranzas.infrastructure.persistence.mappers.deuda_deudor_mapper import (
    mapear_deuda,
    mapear_deudor,
)


def credito_a_fila_acumulado_fin_mes(
    credito: Credito,
    fecha_proceso: date,
    dias_mora_minimo: int,
    archivo_origen: str = "",
) -> FilaAcumuladoFinMes:
    deudor = mapear_deudor(credito)
    deuda = mapear_deuda(credito, archivo_origen=archivo_origen)
    estado_mora = clasificacion_mora_valor(credito, dias_mora_minimo).upper()

    return FilaAcumuladoFinMes(
        fecha_proceso=fecha_proceso,
        deudores_nombre=deudor.nombre.strip(),
        deudores_documento=deudor.documento.strip(),
        deudores_socio=deudor.socio.strip(),
        numero_operacion=deuda.numero_operacion.strip(),
        fecha_corte=deuda.fecha_corte,
        archivo_origen=deuda.archivo_origen.strip(),
        oficina=deuda.oficina.strip(),
        desc_oficina=deuda.desc_oficina.strip(),
        socio=deuda.socio.strip(),
        nombre=deuda.nombre.strip(),
        cedula=deuda.cedula.strip(),
        sector=deuda.sector.strip(),
        tipo_operacion=deuda.tipo_operacion.strip(),
        tipo_destino=deuda.tipo_destino.strip(),
        fecha_concesion=_parsear_fecha(deuda.fecha_concesion),
        fecha_vencimiento=_parsear_fecha(deuda.fecha_vencimiento),
        fecha_ultimo_pago=_parsear_fecha(deuda.fecha_ultimo_pago),
        valor_original_prestamo=deuda.valor_original_prestamo,
        saldo_capital_prestamo=deuda.saldo_capital_prestamo,
        calificacion=deuda.calificacion.strip(),
        total_provision=deuda.total_provision,
        saldo_140x=deuda.saldo_140x,
        saldo_141x=deuda.saldo_141x,
        saldo_142x=deuda.saldo_142x,
        interes_normal=deuda.interes_normal,
        interes_devengado=deuda.interes_devengado,
        interes_vencido=deuda.interes_vencido,
        interes_resolucion=deuda.interes_resolucion,
        interes_castigado=deuda.interes_castigado,
        interes_mora=deuda.interes_mora,
        otros_rubros_deuda=deuda.otros_rubros_deuda,
        total_operacion=deuda.total_operacion,
        estado=deuda.estado.strip(),
        oficial=deuda.oficial.strip(),
        dias_mora=deuda.dias_mora,
        dias_atraso_camorosico=deuda.dias_atraso_camorosico,
        fecha_ingreso=_parsear_fecha(deuda.fecha_ingreso),
        tipo=deuda.tipo.strip(),
        dia_pago=deuda.dia_pago,
        valor_cuota=deuda.valor_cuota,
        cuota_actual=deuda.cuota_actual,
        dividendos=deuda.dividendos,
        cod_oficial_asignado=deuda.cod_oficial_asignado.strip(),
        oficial_asignado=deuda.oficial_asignado.strip(),
        cod_oficial_adm=deuda.cod_oficial_adm.strip(),
        oficial_adm=deuda.oficial_adm.strip(),
        operacion_homologada=deuda.operacion_homologada.strip(),
        decision=deuda.decision.strip(),
        segmentacion=deuda.segmentacion.strip(),
        score=deuda.score.strip(),
        fuente_repago=deuda.fuente_repago.strip(),
        identificacion_ifi=deuda.identificacion_ifi.strip(),
        actividad_economica=deuda.actividad_economica.strip(),
        fecha_archivo=_parsear_fecha(deuda.fecha_archivo),
        tipo_mes=deuda.tipo_mes.strip(),
        tipo_fideicomiso=deuda.tipo_fideicomiso.strip(),
        proceso_cod=deuda.proceso_cod,
        estado_mora=estado_mora,
        id_credito_recblue=(credito.id_credito_recblue or "").strip(),
    )


def _parsear_fecha(valor: str) -> Optional[date]:
    return parsear_fecha_catalogo(valor) if valor else None
