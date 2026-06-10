"""Mapeo Credito / campos TAB → columnas deudores y deuda."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

from cobranzas.domain.models.credito import Credito
from cobranzas.infrastructure.persistence.mappers.cobranza_credito_mapper import valor_tab


@dataclass(frozen=True)
class DeudorPersistencia:
    documento: str
    nombre: str
    socio: str


@dataclass(frozen=True)
class DeudaPersistencia:
    numero_operacion: str
    fecha_corte: Optional[date]
    archivo_origen: str
    oficina: str
    desc_oficina: str
    socio: str
    nombre: str
    cedula: str
    sector: str
    tipo_operacion: str
    tipo_destino: str
    fecha_concesion: str
    fecha_vencimiento: str
    fecha_ultimo_pago: str
    valor_original_prestamo: Optional[Decimal]
    saldo_capital_prestamo: Optional[Decimal]
    calificacion: str
    total_provision: Optional[Decimal]
    saldo_140x: Optional[Decimal]
    saldo_141x: Optional[Decimal]
    saldo_142x: Optional[Decimal]
    interes_normal: Optional[Decimal]
    interes_devengado: Optional[Decimal]
    interes_vencido: Optional[Decimal]
    interes_resolucion: Optional[Decimal]
    interes_castigado: Optional[Decimal]
    interes_mora: Optional[Decimal]
    otros_rubros_deuda: Optional[Decimal]
    total_operacion: Optional[Decimal]
    estado: str
    oficial: str
    dias_mora: Optional[int]
    dias_atraso_camorosico: Optional[int]
    fecha_ingreso: str
    tipo: str
    dia_pago: Optional[int]
    valor_cuota: Optional[Decimal]
    cuota_actual: Optional[int]
    dividendos: Optional[int]
    cod_oficial_asignado: str
    oficial_asignado: str
    cod_oficial_adm: str
    oficial_adm: str
    operacion_homologada: str
    decision: str
    segmentacion: str
    score: str
    fuente_repago: str
    identificacion_ifi: str
    actividad_economica: str
    fecha_archivo: str
    tipo_mes: str
    tipo_fideicomiso: str
    proceso_cod: Optional[int]


def mapear_deudor(credito: Credito) -> DeudorPersistencia:
    documento = (
        credito.cedula
        or valor_tab(credito, "cedula")
        or credito.socio
        or valor_tab(credito, "socio")
        or credito.id_credito
    )
    nombre = (
        credito.cliente
        or valor_tab(credito, "nombre")
        or valor_tab(credito, "nombre_socio")
    )
    socio = credito.socio or valor_tab(credito, "socio")
    return DeudorPersistencia(
        documento=documento.strip(),
        nombre=nombre.strip(),
        socio=socio.strip(),
    )


def mapear_deuda(
    credito: Credito, archivo_origen: str = ""
) -> DeudaPersistencia:
    dias_camorosico = _int_tab(credito, "dias_atraso")
    dias_mora = credito.dias_mora if credito.dias_mora is not None else dias_camorosico

    total_op = _decimal_tab(credito, "total_op", "total_operacion")
    if total_op is None and credito.total_operacion:
        total_op = Decimal(str(credito.total_operacion))

    return DeudaPersistencia(
        numero_operacion=credito.id_credito,
        fecha_corte=credito.fecha_corte,
        archivo_origen=archivo_origen.strip(),
        oficina=valor_tab(credito, "oficina"),
        desc_oficina=(
            valor_tab(credito, "desc_oficina")
            or valor_tab(credito, "des_oficina")
        ),
        socio=credito.socio or valor_tab(credito, "socio"),
        nombre=(
            credito.cliente
            or valor_tab(credito, "nombre")
            or valor_tab(credito, "nombre_socio")
        ),
        cedula=credito.cedula or valor_tab(credito, "cedula"),
        sector=valor_tab(credito, "sector"),
        tipo_operacion=(
            valor_tab(credito, "tipo_oper")
            or valor_tab(credito, "tipo_operacion")
            or credito.tipo_operacion
        ),
        tipo_destino=valor_tab(credito, "tipo_dest") or valor_tab(
            credito, "tipo_destino"
        ),
        fecha_concesion=(
            valor_tab(credito, "fecha_de_concesion")
            or valor_tab(credito, "fecha_concesion")
        ),
        fecha_vencimiento=valor_tab(credito, "fecha_de_vencimiento"),
        fecha_ultimo_pago=valor_tab(credito, "fecha_ultimo_pago"),
        valor_original_prestamo=_decimal_tab(
            credito, "valor_ori_prestam", "valor_total_prest"
        ),
        saldo_capital_prestamo=_decimal_tab(
            credito, "saldo_cap_prest", "saldo_capital_prest"
        ),
        calificacion=valor_tab(credito, "calificac") or credito.calificacion,
        total_provision=_decimal_tab(credito, "total_provision"),
        saldo_140x=_decimal_tab(credito, "saldo_14_0x", "saldo_140x"),
        saldo_141x=_decimal_tab(credito, "saldo_14_1x", "saldo_141x"),
        saldo_142x=_decimal_tab(credito, "saldo_14_2x", "saldo_142x"),
        interes_normal=_decimal_tab(credito, "interes_normal"),
        interes_devengado=_decimal_tab(credito, "int_devengado", "interes_devengado"),
        interes_vencido=_decimal_tab(credito, "int_vencido", "interes_vencido"),
        interes_resolucion=_decimal_tab(
            credito, "int_resolucion", "interes_resolucion"
        ),
        interes_castigado=_decimal_tab(
            credito, "int_castigado", "interes_castigado"
        ),
        interes_mora=_decimal_tab(credito, "interes_mora"),
        otros_rubros_deuda=_decimal_tab(credito, "otros_rubros_deuda"),
        total_operacion=total_op,
        estado=(
            credito.estado_operacion
            or valor_tab(credito, "est")
            or valor_tab(credito, "estado")
        ),
        oficial=(
            credito.nombre_oficial
            or valor_tab(credito, "nombre_oficial")
            or valor_tab(credito, "oficial")
        ),
        dias_mora=dias_mora,
        dias_atraso_camorosico=dias_camorosico,
        fecha_ingreso=valor_tab(credito, "fecha_ingreso"),
        tipo=valor_tab(credito, "tipo"),
        dia_pago=_int_tab(credito, "dia_pago"),
        valor_cuota=_decimal_tab(credito, "valor_cuota"),
        cuota_actual=_int_tab(credito, "cuota_act", "cuota_actual"),
        dividendos=_int_tab(credito, "dividendos"),
        cod_oficial_asignado=(
            credito.codigo_oficial
            or valor_tab(credito, "cod_oficial_asignado")
            or valor_tab(credito, "cod_oficial_asig")
        ),
        oficial_asignado=valor_tab(credito, "oficial_asignado"),
        cod_oficial_adm=valor_tab(credito, "cod_oficial_adm"),
        oficial_adm=valor_tab(credito, "oficial_adm"),
        operacion_homologada=(
            valor_tab(credito, "oper_homologada")
            or valor_tab(credito, "operacion_homologada")
        ),
        decision=valor_tab(credito, "decision"),
        segmentacion=valor_tab(credito, "segmentacion"),
        score=valor_tab(credito, "score"),
        fuente_repago=valor_tab(credito, "fuente_repago"),
        identificacion_ifi=valor_tab(credito, "identificacion_ifi"),
        actividad_economica=valor_tab(credito, "actividad_economica"),
        fecha_archivo=valor_tab(credito, "fecha_archivo"),
        tipo_mes=valor_tab(credito, "tipo_mes"),
        tipo_fideicomiso=valor_tab(credito, "tipo_fideicomiso"),
        proceso_cod=_int_tab(credito, "proceso_cod"),
    )


def _decimal_tab(credito: Credito, *claves: str) -> Optional[Decimal]:
    for clave in claves:
        raw = valor_tab(credito, clave)
        if not raw:
            continue
        try:
            return Decimal(raw.replace(",", ""))
        except Exception:
            continue
    return None


def _int_tab(credito: Credito, *claves: str) -> Optional[int]:
    for clave in claves:
        raw = valor_tab(credito, clave)
        if not raw:
            continue
        try:
            return int(raw.replace(",", "").split(".")[0])
        except ValueError:
            continue
    return None
