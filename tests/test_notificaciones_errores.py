from pathlib import Path
from typing import List, Sequence

import pytest
from openpyxl import Workbook

from cobranzas.domain.models.destinatario_notificacion import DestinatarioNotificacion
from cobranzas.domain.ports.correo_port import CorreoPort
from cobranzas.domain.ports.destinatarios_notificacion_port import (
    DestinatariosNotificacionPort,
)
from cobranzas.domain.services.notificacion_errores_service import NotificacionErroresService
from cobranzas.domain.services.validar_destinatarios_service import (
    ValidacionDestinatariosError,
    validar_destinatarios,
)
from cobranzas.infrastructure.adapters.excel_destinatarios_notificacion_reader import (
    ExcelDestinatariosNotificacionReader,
)


class _CorreoMemoria(CorreoPort):
    def __init__(self) -> None:
        self.envios: List[tuple] = []

    def enviar(
        self,
        destinatarios: Sequence[str],
        asunto: str,
        cuerpo: str,
    ) -> None:
        self.envios.append((list(destinatarios), asunto, cuerpo))


class _ReaderFijo(DestinatariosNotificacionPort):
    def __init__(self, registros: List[DestinatarioNotificacion]) -> None:
        self._registros = registros

    def leer_destinatarios(self, archivo_excel: Path):
        return list(self._registros)


def _crear_excel(path: Path, filas: list[tuple]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    libro = Workbook()
    hoja = libro.active
    for fila in filas:
        hoja.append(fila)
    libro.save(path)


def test_validar_destinatarios_rechaza_email_invalido():
    with pytest.raises(ValidacionDestinatariosError, match="email inválido"):
        validar_destinatarios(
            [DestinatarioNotificacion("A", "no-es-email", True)]
        )


def test_reader_excel_notificaciones(tmp_path: Path):
    archivo = tmp_path / "notificaciones.xlsx"
    _crear_excel(
        archivo,
        [
            ("nombre", "email", "activo"),
            ("Ana", "ana@test.com", "si"),
            ("Bob", "bob@test.com", "no"),
        ],
    )
    registros = ExcelDestinatariosNotificacionReader().leer_destinatarios(archivo)
    assert len(registros) == 2
    assert registros[0].email == "ana@test.com"
    assert registros[1].activo is False


def test_servicio_envia_solo_activos(tmp_path: Path):
    correo = _CorreoMemoria()
    servicio = NotificacionErroresService(
        destinatarios_reader=_ReaderFijo(
            [
                DestinatarioNotificacion("Ana", "ana@test.com", True),
                DestinatarioNotificacion("Bob", "bob@test.com", False),
            ]
        ),
        correo=correo,
        archivo_excel=tmp_path / "x.xlsx",
    )
    resultado = servicio.notificar_fallo(
        "pipeline",
        ["archivo no encontrado"],
        fecha_corte="06042026",
    )
    assert resultado.enviado is True
    assert resultado.destinatarios == ["ana@test.com"]
    assert len(correo.envios) == 1
    assert "archivo no encontrado" in correo.envios[0][2]
