from datetime import date

from cobranzas.domain.models.credito import Credito
from cobranzas.domain.ports.asignacion_mensual_port import AsignacionMensualPort
from cobranzas.domain.ports.asesores_rotacion_port import AsesoresRotacionPort
from cobranzas.domain.services.asignacion_cartera_service import AsignacionCarteraService


class _RotacionFija(AsesoresRotacionPort):
    def __init__(self, asesores):
        self._asesores = asesores

    def listar_activos(self):
        return list(self._asesores)


class _MesFijo(AsignacionMensualPort):
    """Asignaciones por (año, mes) como en BD asesores_deuda."""

    def __init__(self, por_mes: dict):
        self._por_mes = por_mes

    def asignaciones_del_mes(self, anio: int, mes: int):
        return dict(self._por_mes.get((anio, mes), {}))


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


def test_ultimo_dia_mes_sin_asignacion_solo_historial():
    servicio = AsignacionCarteraService(
        asesores_rotacion=_RotacionFija([("A", "Asesor A")]),
    )
    creditos = [Credito("001", "C", 100.0, 1, date(2026, 6, 30))]
    out, filas = servicio.asignar(creditos, date(2026, 6, 30))
    assert filas == []
    assert not out[0].codigo_oficial
    assert not out[0].nombre_oficial


def test_primer_dia_mes_reasigna_aunque_bd_tenga_mes_actual():
    """Día 1 del mes: reasignación completa; ignora asignaciones del mes en BD."""
    servicio = AsignacionCarteraService(
        asesores_rotacion=_RotacionFija([("A", "Asesor A"), ("B", "Asesor B")]),
        asignacion_mensual=_MesFijo(
            {(2026, 6): {"001": ("Z", "Junio previo"), "002": ("Z", "Junio previo")}},
        ),
    )
    creditos = [
        Credito("001", "C1", 100.0, 1, date(2026, 6, 1)),
        Credito("002", "C2", 90.0, 1, date(2026, 6, 1)),
    ]
    _, filas = servicio.asignar(creditos, date(2026, 6, 1))
    assert [f.codigo_asesor for f in filas] == ["A", "B"]
    assert all(f.reasignado for f in filas)


def test_mes_nuevo_sin_asignaciones_previas_rota_todos():
    """Primer corte de julio: BD sin julio → asignación nueva para todos."""
    servicio = AsignacionCarteraService(
        asesores_rotacion=_RotacionFija([("A", "Asesor A"), ("B", "Asesor B")]),
        asignacion_mensual=_MesFijo(
            {(2026, 6): {"001": ("Z", "Junio")}},
        ),
    )
    creditos = [
        Credito("001", "C1", 100.0, 1, date(2026, 7, 1)),
        Credito("002", "C2", 90.0, 1, date(2026, 7, 1)),
    ]
    _, filas = servicio.asignar(creditos, date(2026, 7, 1))
    assert [f.codigo_asesor for f in filas] == ["A", "B"]
    assert all(f.reasignado for f in filas)


def test_mismo_mes_segunda_consulta_mantiene_asesor():
    """Re-ejecutar en julio con asignación ya en BD → no reasigna."""
    servicio = AsignacionCarteraService(
        asesores_rotacion=_RotacionFija([("A", "Asesor A"), ("B", "Asesor B")]),
        asignacion_mensual=_MesFijo(
            {(2026, 7): {"001": ("Z", "Julio previo")}},
        ),
    )
    creditos = [
        Credito("001", "C1", 100.0, 1, date(2026, 7, 1)),
        Credito("002", "C2", 90.0, 1, date(2026, 7, 6)),
    ]
    _, filas = servicio.asignar(creditos, date(2026, 7, 6))
    assert filas[0].codigo_asesor == "Z"
    assert filas[0].reasignado is False
    assert filas[1].codigo_asesor == "B"
    assert filas[1].reasignado is True


def test_dia_intermedio_mantiene_asignacion_del_mes():
    servicio = AsignacionCarteraService(
        asesores_rotacion=_RotacionFija([("A", "Asesor A"), ("B", "Asesor B")]),
        asignacion_mensual=_MesFijo({(2026, 4): {"001": ("Z", "Anterior")}}),
    )
    creditos = [
        Credito("001", "C1", 100.0, 1, date(2026, 4, 3)),
        Credito("002", "C2", 90.0, 1, date(2026, 4, 3)),
    ]
    _, filas = servicio.asignar(creditos, date(2026, 4, 3))
    assert filas[0].codigo_asesor == "Z"
    assert filas[0].reasignado is False
    assert filas[1].codigo_asesor == "B"
    assert filas[1].reasignado is True


def test_dia_anterior_tras_dia_posterior_cero_nuevas():
    """Día 5 asigna; re-ejecutar día 4 → 0 nuevas (comparar con BD del mes)."""
    servicio = AsignacionCarteraService(
        asesores_rotacion=_RotacionFija([("A", "Asesor A"), ("B", "Asesor B")]),
        asignacion_mensual=_MesFijo(
            {
                (2026, 6): {
                    "001": ("A", "Junio 5"),
                    "002": ("B", "Junio 5"),
                }
            },
        ),
    )
    creditos = [
        Credito("001", "C1", 100.0, 1, date(2026, 6, 4)),
        Credito("002", "C2", 90.0, 1, date(2026, 6, 4)),
    ]
    _, filas = servicio.asignar(creditos, date(2026, 6, 4))
    assert all(not f.reasignado for f in filas)
    assert [f.codigo_asesor for f in filas] == ["A", "B"]


def test_falla_si_no_hay_asesores_activos_en_bd():
    import pytest

    servicio = AsignacionCarteraService(asesores_rotacion=_RotacionFija([]))
    with pytest.raises(ValueError, match="asesores activos"):
        servicio.asignar([Credito("001", "C", 100.0, 3, date(2026, 6, 2))], date(2026, 6, 2))
