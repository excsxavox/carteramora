from datetime import date
from unittest.mock import MagicMock

from cobranzas.application.chain.asignacion_handler import AsignacionHandler
from cobranzas.application.chain.proceso_context import ProcesoContext
from cobranzas.domain.models.credito import Credito


def test_ultimo_dia_mes_servicio_devuelve_sin_filas():
    servicio = MagicMock()
    servicio.asignar.return_value = ([], [])
    handler = AsignacionHandler(servicio)
    credito = Credito("001", "C", 100.0, 1, date(2026, 6, 30))
    contexto = ProcesoContext(dias_mora_minimo=1, usar_mora_temprana=True)
    contexto.creditos = [credito]

    resultado = handler._procesar(contexto)

    servicio.asignar.assert_called_once_with([credito], date(2026, 6, 30))
    assert resultado.asignaciones == []


def test_dia_6_asigna_y_guarda_filas():
    servicio = MagicMock()
    credito_asignado = Credito(
        "001", "C", 100.0, 1, date(2026, 4, 6), codigo_oficial="A"
    )
    fila = MagicMock()
    servicio.asignar.return_value = ([credito_asignado], [fila])
    handler = AsignacionHandler(servicio)
    credito = Credito("001", "C", 100.0, 1, date(2026, 4, 6))
    contexto = ProcesoContext(dias_mora_minimo=1, usar_mora_temprana=True)
    contexto.creditos = [credito]

    resultado = handler._procesar(contexto)

    assert resultado.creditos == [credito_asignado]
    assert resultado.asignaciones == [fila]
