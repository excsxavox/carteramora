"""Utilidad central para alertar errores del pipeline por correo."""

import traceback
from typing import Optional, Sequence

from cobranzas.domain.models.notificacion_resultado import NotificacionResultado
from cobranzas.infrastructure.config.settings import Settings
from cobranzas.jobs.notificaciones_container import build_notificacion_errores_service


def notificar_error_pipeline(
    settings: Settings,
    origen: str,
    mensajes: Sequence[str],
    *,
    fecha_corte: str = "",
    exc: Optional[BaseException] = None,
) -> NotificacionResultado:
    """
    Lee destinatarios del Excel y envía correo si las notificaciones están habilitadas.
  """
    servicio = build_notificacion_errores_service(settings)
    if servicio is None:
        motivo = "notificaciones deshabilitadas"
        if settings.notificaciones_errores_habilitado:
            motivo = "SMTP no configurado o notificaciones deshabilitadas"
        return NotificacionResultado(omitido_motivo=motivo)

    traceback_text = ""
    if exc is not None:
        traceback_text = "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        )

    return servicio.notificar_fallo(
        origen=origen,
        mensajes=list(mensajes),
        fecha_corte=fecha_corte,
        traceback_text=traceback_text,
    )
