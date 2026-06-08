from dataclasses import dataclass


@dataclass(frozen=True)
class DestinatarioNotificacion:
    """Destinatario de alertas por correo (errores del pipeline)."""

    nombre: str
    email: str
    activo: bool = True
