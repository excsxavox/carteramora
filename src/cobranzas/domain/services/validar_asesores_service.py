import re
from typing import Dict, List, Tuple

from cobranzas.domain.models.asesor_registro import AsesorRegistro

PATRON_CEDULA_ASESOR = re.compile(r"^OF-[A-Z0-9]+$", re.IGNORECASE)
PATRON_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ValidacionAsesoresError(ValueError):
    """El Excel o los registros no pasan las validaciones anti-duplicado."""


def validar_registros_asesores(
    registros: List[AsesorRegistro],
    *,
    rechazar_duplicados_excel: bool = True,
) -> Tuple[List[AsesorRegistro], List[str]]:
    """
    Valida y deduplica por cédula.
    Retorna (registros_unicos, advertencias).
    Lanza ValidacionAsesoresError si hay duplicados y rechazar_duplicados_excel=True.
    """
    advertencias: List[str] = []
    errores: List[str] = []

    por_cedula: Dict[str, List[int]] = {}
    por_email: Dict[str, List[str]] = {}

    for indice, registro in enumerate(registros, start=1):
        _validar_campos_registro(registro, indice, errores)
        por_cedula.setdefault(registro.cedula, []).append(indice)
        if registro.email:
            clave_email = registro.email.strip().lower()
            por_email.setdefault(clave_email, []).append(registro.cedula)

    _validar_duplicados_cedula(por_cedula, rechazar_duplicados_excel, errores, advertencias)
    _validar_emails_duplicados(por_email, advertencias)

    if errores:
        raise ValidacionAsesoresError("\n".join(errores))

    unicos = _deduplicar_por_cedula(registros, advertencias)
    return unicos, advertencias


def _validar_campos_registro(registro: AsesorRegistro, indice: int, errores: List[str]) -> None:
    if not PATRON_CEDULA_ASESOR.match(registro.cedula):
        errores.append(
            f"Fila {indice}: cédula inválida '{registro.cedula}' "
            f"(use código oficial, ej. 087 u OF-87)"
        )
    if len(registro.nombre.strip()) < 3:
        errores.append(f"Fila {indice}: nombre demasiado corto o vacío")
    if registro.email and not PATRON_EMAIL.match(registro.email.strip()):
        errores.append(f"Fila {indice}: email inválido '{registro.email}'")


def _validar_duplicados_cedula(
    por_cedula: Dict[str, List[int]],
    rechazar: bool,
    errores: List[str],
    advertencias: List[str],
) -> None:
    for cedula, filas in por_cedula.items():
        if len(filas) <= 1:
            continue
        mensaje = (
            f"Cédula duplicada en Excel '{cedula}' en filas: "
            + ", ".join(str(f) for f in filas)
        )
        if rechazar:
            errores.append(mensaje)
        else:
            advertencias.append(f"{mensaje} (se usará la última fila)")


def _validar_emails_duplicados(
    por_email: Dict[str, List[str]],
    advertencias: List[str],
) -> None:
    for email, cedulas in por_email.items():
        unicas = list(dict.fromkeys(cedulas))
        if len(unicas) > 1:
            advertencias.append(
                f"Email '{email}' repetido con cédulas distintas: {', '.join(unicas)}"
            )


def _deduplicar_por_cedula(
    registros: List[AsesorRegistro],
    advertencias: List[str],
) -> List[AsesorRegistro]:
    vistos: Dict[str, AsesorRegistro] = {}
    for registro in registros:
        if registro.cedula in vistos:
            advertencias.append(
                f"Cédula {registro.cedula}: fila duplicada omitida "
                f"(se conserva '{vistos[registro.cedula].nombre}')"
            )
        vistos[registro.cedula] = registro
    return list(vistos.values())


def registro_igual_a_bd(registro: AsesorRegistro, asesor) -> bool:
    """True si no hay cambios respecto al asesor ya guardado."""
    tel_bd = (asesor.numero_telefono or "").strip()
    tel_reg = (registro.numero_telefono or "").strip()
    email_bd = (asesor.email or "").strip().lower()
    email_reg = (registro.email or "").strip().lower()
    return (
        (asesor.nombre or "").strip() == registro.nombre.strip()
        and tel_bd == tel_reg
        and email_bd == email_reg
        and bool(asesor.activo) == registro.activo
    )
