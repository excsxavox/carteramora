from decimal import Decimal
from typing import Optional, Tuple

from cobranzas.domain.models.credito import Credito, EstadoMora

CLAVE_CLASIFICACION_MORA = "CLASIFICACION_MORA"
PREFIJO_CEDULA_ASESOR = "OF-"


def valor_tab(credito: Credito, clave: str) -> str:
    return credito.campos_tab_dict().get(clave, "").strip()


def codigo_asesor(credito: Credito) -> str:
    return (
        credito.codigo_oficial
        or valor_tab(credito, "oficial")
        or valor_tab(credito, "cod_oficial_asignado")
    ).strip()


def nombre_asesor(credito: Credito) -> str:
    return (
        credito.nombre_oficial
        or valor_tab(credito, "nombre_oficial")
        or valor_tab(credito, "oficial_asignado")
    ).strip()


def cedula_asesor(codigo: str) -> str:
    return f"{PREFIJO_CEDULA_ASESOR}{codigo}"


def montos_desde_credito(credito: Credito) -> Tuple[Decimal, Decimal, Decimal]:
    total_op = (
        Decimal(str(credito.total_operacion))
        if credito.total_operacion
        else _decimal_tab(credito, "valor_total_prest", "total_op", "total_operacion")
    )
    total_atrasado = (
        Decimal(str(credito.total_atrasado))
        if credito.total_atrasado
        else _decimal_tab(credito, "total_atrasado")
    )
    monto_mora = Decimal(str(credito.saldo_pendiente or 0))
    return total_atrasado, total_op, monto_mora


def _decimal_tab(credito: Credito, *claves: str) -> Decimal:
    for clave in claves:
        raw = valor_tab(credito, clave)
        if raw:
            try:
                return Decimal(raw.replace(",", ""))
            except Exception:
                continue
    return Decimal("0")


def clasificacion_mora_valor(credito: Credito, dias_mora_minimo: int) -> str:
    return credito.clasificar_mora(dias_mora_minimo).value


def estado_operacion_valor(credito: Credito) -> str:
    return (
        credito.estado_operacion
        or valor_tab(credito, "estado")
        or valor_tab(credito, "est")
    ).strip()


def catalogo_descripcion_clasificacion(estado: EstadoMora) -> str:
    return {
        EstadoMora.AL_DIA: "Operación al día",
        EstadoMora.MORA_LEVE: "Mora leve",
        EstadoMora.MORA_GRAVE: "Mora grave",
    }.get(estado, "Clasificación de mora")
