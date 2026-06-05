from decimal import Decimal
from typing import Optional, Tuple

from cobranzas.domain.models.credito import Credito, EstadoMora

CLAVE_CLASIFICACION_MORA = "CLASIFICACION_MORA"
PREFIJO_CEDULA_ASESOR = "OF-"
ESTADO_ASESOR_MORA_TEMPRANA = "MORA_TEMPRANA"
ESTADO_ASESOR_MORA_MADURA = "MORA_MADURA"
CATALOGO_MORA_TEMPRANA = "mora_temprana"


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


def codigo_usuario_desde_cedula_asesor(cedula: str) -> str:
    """OF-520 → 520; AMOLINA → AMOLINA (usuario Recblue / asignación)."""
    texto = (cedula or "").strip().upper()
    if texto.startswith(PREFIJO_CEDULA_ASESOR):
        return texto[len(PREFIJO_CEDULA_ASESOR) :].strip()
    return texto


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


def clasificacion_para_asignacion(
    credito: Credito,
    dias_mora_minimo: int,
    usar_mora_temprana: bool = False,
    mora_temprana_dias_min: int = 1,
    mora_temprana_dias_max: int = 29,
) -> Tuple[str, str, str]:
    """
    Clasificación de cobranza para asesores_deuda.

    Retorna (valor_catalogo, descripcion_catalogo, estado_asesores_deuda).
    El estado operativo del crédito (VIGENTE, CASTIGADO…) queda en deuda.estado.
    """
    if (
        usar_mora_temprana
        and mora_temprana_dias_min <= credito.dias_mora <= mora_temprana_dias_max
    ):
        return (
            CATALOGO_MORA_TEMPRANA,
            "Mora temprana",
            ESTADO_ASESOR_MORA_TEMPRANA,
        )

    estado = credito.clasificar_mora(dias_mora_minimo)
    if estado == EstadoMora.MORA_GRAVE:
        estado_asesor = EstadoMora.MORA_GRAVE.value.upper()
    elif estado == EstadoMora.MORA_LEVE:
        estado_asesor = ESTADO_ASESOR_MORA_MADURA
    else:
        estado_asesor = EstadoMora.AL_DIA.value.upper()

    return (
        clasificacion_mora_valor(credito, dias_mora_minimo),
        catalogo_descripcion_clasificacion(estado),
        estado_asesor,
    )


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
