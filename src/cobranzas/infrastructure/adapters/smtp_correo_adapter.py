import logging
import smtplib
from email.message import EmailMessage
from typing import Optional, Sequence

from cobranzas.domain.ports.correo_port import CorreoPort

logger = logging.getLogger("cobranzas.notificaciones.smtp")


class SmtpCorreoAdapter(CorreoPort):
    def __init__(
        self,
        host: str,
        port: int,
        usuario: Optional[str] = None,
        password: Optional[str] = None,
        remitente: Optional[str] = None,
        usar_tls: bool = True,
        usar_ssl: bool = False,
    ) -> None:
        if not host:
            raise ValueError("SMTP_HOST es obligatorio para enviar correos")
        self._host = host
        self._port = port
        self._usuario = usuario
        self._password = password
        self._remitente = remitente or usuario
        if not self._remitente:
            raise ValueError("SMTP_FROM o SMTP_USER es obligatorio para enviar correos")
        self._usar_tls = usar_tls
        self._usar_ssl = usar_ssl

    def enviar(
        self,
        destinatarios: Sequence[str],
        asunto: str,
        cuerpo: str,
    ) -> None:
        if not destinatarios:
            raise ValueError("Sin destinatarios para el correo")

        mensaje = EmailMessage()
        mensaje["From"] = self._remitente
        mensaje["To"] = ", ".join(destinatarios)
        mensaje["Subject"] = asunto
        mensaje.set_content(cuerpo)

        if self._usar_ssl:
            with smtplib.SMTP_SSL(self._host, self._port, timeout=30) as smtp:
                self._autenticar(smtp)
                smtp.send_message(mensaje)
            return

        with smtplib.SMTP(self._host, self._port, timeout=30) as smtp:
            if self._usar_tls:
                smtp.starttls()
            self._autenticar(smtp)
            smtp.send_message(mensaje)

        logger.debug(
            "Correo enviado vía %s:%s a %s destinatario(s)",
            self._host,
            self._port,
            len(destinatarios),
        )

    def _autenticar(self, smtp: smtplib.SMTP) -> None:
        if self._usuario and self._password:
            smtp.login(self._usuario, self._password)
