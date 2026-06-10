from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

from cobranzas.application.chain.export_asignacion_handler import ExportAsignacionHandler
from cobranzas.application.chain.proceso_context import ProcesoContext
from cobranzas.domain.models.asignacion_credito import AsignacionCredito
from cobranzas.domain.models.credito import Credito


def _contexto(fecha: date, con_asignacion: bool = True) -> ProcesoContext:
    credito = Credito("001", "Cliente", 100.0, 1, fecha)
    ctx = ProcesoContext(dias_mora_minimo=1, usar_mora_temprana=True)
    ctx.creditos = [credito]
    ctx.creditos_mora = [credito]
    ctx.archivo_asignacion = Path("destino/ASIGNACION.csv")
    if con_asignacion:
        ctx.asignaciones = [
            AsignacionCredito(
                fecha_corte=fecha,
                numero_operacion="001",
                identificacion="",
                socio="",
                nombre="Cliente",
                saldo_capital=100.0,
                dias_mora=1,
                codigo_asesor="A",
                nombre_asesor="Asesor A",
            )
        ]
    return ctx


def test_ultimo_dia_mes_no_exporta_asignacion_csv():
    export = MagicMock()
    handler = ExportAsignacionHandler(export)
    contexto = _contexto(date(2026, 6, 30))

    resultado = handler._procesar(contexto)

    export.exportar_csv.assert_not_called()
    assert resultado is contexto


def test_dia_1_exporta_asignacion_csv():
    export = MagicMock()
    handler = ExportAsignacionHandler(export)
    contexto = _contexto(date(2026, 7, 1))

    handler._procesar(contexto)

    export.exportar_csv.assert_called_once()
    args, kwargs = export.exportar_csv.call_args
    assert args[0] == contexto.archivo_asignacion
    assert len(args[1]) == 1


def test_dia_6_exporta_asignacion_csv():
    export = MagicMock()
    handler = ExportAsignacionHandler(export)
    contexto = _contexto(date(2026, 4, 6))

    handler._procesar(contexto)

    export.exportar_csv.assert_called_once()
