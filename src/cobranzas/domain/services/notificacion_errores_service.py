"""Envío de alertas por correo cuando falla el pipeline."""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Sequence

from cobranzas.domain.models.notificacion_resultado import NotificacionResultado
from cobranzas.domain.ports.correo_port import CorreoPort
from cobranzas.domain.ports.destinatarios_notificacion_port import (
    DestinatariosNotificacionPort,
)
from cobranzas.domain.services.validar_destinatarios_service import (
    ValidacionDestinatariosError,
    validar_destinatarios,
)

logger = logging.getLogger("cobranzas.notificaciones")


class NotificacionErroresService:
    def __init__(
        self,
        destinatarios_reader: DestinatariosNotificacionPort,
        correo: CorreoPort,
        archivo_excel: Path,
        asunto_prefijo: str = "[Cartera Mora]",
    ) -> None:
        self._reader = destinatarios_reader
        self._correo = correo
        self._archivo_excel = archivo_excel
        self._asunto_prefijo = asunto_prefijo.strip() or "[Cartera Mora]"

    def notificar_fallo(
        self,
        origen: str,
        mensajes: Sequence[str],
        *,
        fecha_corte: str = "",
        traceback_text: str = "",
    ) -> NotificacionResultado:
        resultado = NotificacionResultado()
        try:
            registros_raw = self._reader.leer_destinatarios(self._archivo_excel)
            registros, advertencias = validar_destinatarios(registros_raw)
            for aviso in advertencias:
                logger.warning("Notificaciones: %s", aviso)
        except FileNotFoundError as exc:
            resultado.omitido_motivo = str(exc)
            logger.error("Notificaciones: %s", exc)
            return resultado
        except ValidacionDestinatariosError as exc:
            resultado.errores.append(str(exc))
            logger.error("Excel de notificaciones inválido:\n%s", exc)
            return resultado
        except Exception as exc:
            resultado.errores.append(str(exc))
            logger.exception("Error leyendo destinatarios de notificación")
            return resultado

        activos = [r for r in registros if r.activo]
        correos = [r.email for r in activos]
        if not correos:
            resultado.omitido_motivo = "sin destinatarios activos en Excel"
            logger.warning("Notificaciones: %s", resultado.omitido_motivo)
            return resultado

        asunto = f"{self._asunto_prefijo} Error en {origen}"
        cuerpo = self._construir_cuerpo(
            origen=origen,
            mensajes=mensajes,
            fecha_corte=fecha_corte,
            traceback_text=traceback_text,
        )

        try:
            self._correo.enviar(correos, asunto, cuerpo)
            resultado.enviado = True
            resultado.destinatarios = correos
            logger.info(
                "Alerta de error enviada | destinatarios=%s | origen=%s",
                len(correos),
                origen,
            )
        except Exception as exc:
            resultado.errores.append(str(exc))
            logger.exception("No se pudo enviar correo de error")
        return resultado

    def _construir_cuerpo(
        self,
        origen: str,
        mensajes: Sequence[str],
        fecha_corte: str,
        traceback_text: str,
    ) -> str:
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lineas = [
            "Se detectó un error en el procesamiento de cartera en mora.",
            "",
            f"Fecha/hora: {ahora}",
            f"Origen: {origen}",
        ]
        if fecha_corte:
            lineas.append(f"Fecha de corte: {fecha_corte}")
        lineas.extend(["", "Detalle del error:", ""])
        if mensajes:
            lineas.extend(f"- {msg}" for msg in mensajes)
        else:
            lineas.append("- Sin mensaje adicional")
        if traceback_text:
            lineas.extend(["", "Traza técnica:", "", traceback_text])
        lineas.extend(
            [
                "",
                "---",
                "Este mensaje fue generado automáticamente por el job de cobranzas.",
                f"Destinatarios configurados en: {self._archivo_excel.as_posix()}",
            ]
        )
        return "\n".join(lineas)
