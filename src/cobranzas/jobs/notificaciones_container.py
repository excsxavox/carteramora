"""Composition root para alertas por correo."""

import logging
from typing import Optional

from cobranzas.domain.services.notificacion_errores_service import NotificacionErroresService
from cobranzas.infrastructure.adapters.excel_destinatarios_notificacion_reader import (
    ExcelDestinatariosNotificacionReader,
)
from cobranzas.infrastructure.adapters.smtp_correo_adapter import SmtpCorreoAdapter
from cobranzas.infrastructure.config.settings import Settings

logger = logging.getLogger("cobranzas.notificaciones")


def build_notificacion_errores_service(
    settings: Optional[Settings] = None,
) -> Optional[NotificacionErroresService]:
    cfg = settings or Settings()
    if not cfg.notificaciones_errores_habilitado:
        return None

    if not (cfg.smtp_host or "").strip():
        logger.warning(
            "NOTIFICACIONES_ERRORES_HABILITADO=true pero SMTP_HOST no está "
            "configurado; se omiten correos de error"
        )
        return None

    correo = SmtpCorreoAdapter(
        host=cfg.smtp_host or "",
        port=cfg.smtp_port,
        usuario=cfg.smtp_user,
        password=cfg.smtp_password,
        remitente=cfg.smtp_from,
        usar_tls=cfg.smtp_use_tls,
        usar_ssl=cfg.smtp_use_ssl,
    )
    return NotificacionErroresService(
        destinatarios_reader=ExcelDestinatariosNotificacionReader(),
        correo=correo,
        archivo_excel=cfg.archivo_excel_notificaciones,
        asunto_prefijo=cfg.notificaciones_asunto_prefijo,
    )
