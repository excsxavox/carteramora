"""Mapeo Credito / campos TAB → columnas deudores y deuda."""

from dataclasses import dataclass
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
    oficina: str
    descripcion_oficina: str
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
    saldo: Optional[Decimal]


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


def mapear_deuda(credito: Credito) -> DeudaPersistencia:
    return DeudaPersistencia(
        numero_operacion=credito.id_credito,
        oficina=valor_tab(credito, "oficina"),
        descripcion_oficina=(
            valor_tab(credito, "des_oficina")
            or valor_tab(credito, "desc_oficina")
        ),
        sector=valor_tab(credito, "sector"),
        tipo_operacion=(
            valor_tab(credito, "tipo_oper")
            or valor_tab(credito, "tipo_operacion")
            or credito.tipo_operacion
        ),
        tipo_destino=valor_tab(credito, "tipo_dest"),
        fecha_concesion=(
            valor_tab(credito, "fecha_de_concesion")
            or valor_tab(credito, "fecha_concesion")
        ),
        fecha_vencimiento=valor_tab(credito, "fecha_de_vencimiento"),
        fecha_ultimo_pago=valor_tab(credito, "fecha_ultimo_pago"),
        valor_original_prestamo=_decimal_tab(
            credito, "valor_ori_prestam", "valor_total_prest", "total_operacion"
        ),
        saldo_capital_prestamo=_decimal_tab(
            credito, "saldo_cap_prest", "saldo_capital_prest"
        ),
        calificacion=valor_tab(credito, "calificac") or credito.calificacion,
        total_provision=_decimal_tab(credito, "total_provision"),
        saldo=_decimal_tab(
            credito,
            "saldo_cap_prest",
            "saldo_capital_prest",
            "saldo_capital_atrasado",
            "total_op",
        ),
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
    if claves and claves[0] == "total_operacion" and credito.total_operacion:
        return Decimal(str(credito.total_operacion))
    return None
