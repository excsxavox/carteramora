import re
from typing import List, Tuple

from cobranzas.domain.models.destinatario_notificacion import DestinatarioNotificacion

PATRON_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ValidacionDestinatariosError(ValueError):
    """El Excel de notificaciones no cumple las validaciones."""


def validar_destinatarios(
    registros: List[DestinatarioNotificacion],
) -> Tuple[List[DestinatarioNotificacion], List[str]]:
    """
    Valida correos y deduplica por email (case-insensitive).
    Retorna (registros_unicos, advertencias).
    """
    advertencias: List[str] = []
    errores: List[str] = []
    vistos: dict[str, str] = {}
    unicos: List[DestinatarioNotificacion] = []

    for indice, registro in enumerate(registros, start=1):
        email = (registro.email or "").strip()
        nombre = (registro.nombre or "").strip()

        if not email:
            errores.append(f"Fila {indice}: falta email")
            continue
        if not PATRON_EMAIL.match(email):
            errores.append(f"Fila {indice}: email inválido '{email}'")
            continue
        if not nombre:
            errores.append(f"Fila {indice}: falta nombre para '{email}'")
            continue

        clave = email.lower()
        if clave in vistos:
            advertencias.append(
                f"Email duplicado omitido: '{email}' (ya registrado como {vistos[clave]})"
            )
            continue

        vistos[clave] = nombre
        unicos.append(
            DestinatarioNotificacion(
                nombre=nombre,
                email=email,
                activo=registro.activo,
            )
        )

    if errores:
        raise ValidacionDestinatariosError("\n".join(errores))

    return unicos, advertencias
