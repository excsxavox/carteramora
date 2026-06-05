from datetime import date

from cobranzas.domain.models.credito import Credito
from cobranzas.domain.ports.asesores_rotacion_port import AsesoresRotacionPort
from cobranzas.domain.services.asignacion_cartera_service import AsignacionCarteraService


class _RotacionFija(AsesoresRotacionPort):
    def __init__(self, asesores):
        self._asesores = asesores

    def listar_activos(self):
        return list(self._asesores)


def test_rotacion_secuencial_desde_bd():
    servicio = AsignacionCarteraService(
        asesores_rotacion=_RotacionFija([("A", "Asesor A"), ("B", "Asesor B")]),
    )
    creditos = [
        Credito(
            f"00{i}",
            f"C{i}",
            1000 - i,
            5,
            date(2026, 6, 2),
            campos_tab=(("saldo_cap_prest", str(1000 - i)),),
        )
        for i in range(3)
    ]
    _, filas = servicio.asignar(creditos, date(2026, 6, 2))
    assert [f.codigo_asesor for f in filas] == ["A", "B", "A"]
    assert [f.nombre_asesor for f in filas] == ["Asesor A", "Asesor B", "Asesor A"]


def test_falla_si_no_hay_asesores_activos_en_bd():
    import pytest

    servicio = AsignacionCarteraService(asesores_rotacion=_RotacionFija([]))
    with pytest.raises(ValueError, match="asesores activos"):
        servicio.asignar([Credito("001", "C", 100.0, 3, date(2026, 6, 2))], date(2026, 6, 2))
