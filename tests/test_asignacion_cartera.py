from datetime import date

from cobranzas.domain.models.credito import Credito
from cobranzas.domain.services.asignacion_cartera_service import AsignacionCarteraService


def test_rotacion_secuencial():
    servicio = AsignacionCarteraService(
        rotacion_asesores=("A", "B"),
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
