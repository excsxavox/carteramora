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

    def asignaciones_del_mes(self, anio: int, mes: int, excluir_fecha=None):
        return dict(self._por_mes.get((anio, mes), {}))


class _MesPorFecha(AsignacionMensualPort):
    """Asignaciones con fecha de corte, para validar exclusión del propio corte."""

    def __init__(self, por_fecha: dict):
        # por_fecha: {date: {op: (codigo, nombre)}}
        self._por_fecha = por_fecha

    def asignaciones_del_mes(self, anio: int, mes: int, excluir_fecha=None):
        resultado: dict = {}
        for fecha, asignaciones in self._por_fecha.items():
            if fecha.year != anio or fecha.month != mes:
                continue
            if excluir_fecha is not None and fecha == excluir_fecha:
                continue
            resultado.update(asignaciones)
        return resultado


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


def test_primer_dia_mes_conserva_fin_de_mes_anterior():
    """Día 1: conserva el asesor del cierre del mes anterior; no reasigna esas."""
    servicio = AsignacionCarteraService(
        asesores_rotacion=_RotacionFija([("A", "Asesor A"), ("B", "Asesor B")]),
        asignacion_mensual=_MesFijo(
            {(2026, 5): {"001": ("Z", "Mayo cierre"), "002": ("Z", "Mayo cierre")}},
        ),
    )
    creditos = [
        Credito("001", "C1", 100.0, 1, date(2026, 6, 1)),
        Credito("002", "C2", 90.0, 1, date(2026, 6, 1)),
    ]
    _, filas = servicio.asignar(creditos, date(2026, 6, 1))
    assert [f.codigo_asesor for f in filas] == ["Z", "Z"]
    assert all(not f.reasignado for f in filas)


def test_primer_dia_mes_solo_rota_las_nuevas():
    """Día 1: conserva las del cierre anterior y solo rota las NUEVAS."""
    servicio = AsignacionCarteraService(
        asesores_rotacion=_RotacionFija([("A", "Asesor A"), ("B", "Asesor B")]),
        asignacion_mensual=_MesFijo(
            {(2026, 6): {"001": ("Z", "Junio cierre")}},
        ),
    )
    creditos = [
        Credito("001", "C1", 100.0, 1, date(2026, 7, 1)),
        Credito("002", "C2", 90.0, 1, date(2026, 7, 1)),
    ]
    _, filas = servicio.asignar(creditos, date(2026, 7, 1))
    assert filas[0].codigo_asesor == "Z"
    assert filas[0].reasignado is False
    assert filas[1].codigo_asesor == "B"
    assert filas[1].reasignado is True


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


def test_dia_2_solo_asigna_nuevos_en_mora_temprana():
    """Día 2+: conserva mes en BD; solo rota operaciones nuevas elegibles."""
    servicio = AsignacionCarteraService(
        asesores_rotacion=_RotacionFija([("A", "Asesor A"), ("B", "Asesor B")]),
        asignacion_mensual=_MesFijo(
            {(2026, 6): {"001": ("Z", "Día 1")}},
        ),
    )
    creditos = [
        Credito("001", "C1", 100.0, 1, date(2026, 6, 2)),
        Credito("002", "C2", 90.0, 1, date(2026, 6, 2)),
    ]
    _, filas = servicio.asignar(creditos, date(2026, 6, 2))
    assert filas[0].codigo_asesor == "Z"
    assert not filas[0].reasignado
    assert filas[1].codigo_asesor == "B"
    assert filas[1].reasignado


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


def test_reproceso_mismo_corte_recalcula_como_nuevas():
    """Re-ejecutar el MISMO corte (ya en BD) debe recalcular sus asignaciones
    como nuevas: su propia asignación previa no cuenta como conservada."""
    servicio = AsignacionCarteraService(
        asesores_rotacion=_RotacionFija([("A", "Asesor A"), ("B", "Asesor B")]),
        asignacion_mensual=_MesPorFecha(
            {date(2026, 6, 2): {"001": ("Z", "Previo"), "002": ("Z", "Previo")}},
        ),
    )
    creditos = [
        Credito("001", "C1", 100.0, 1, date(2026, 6, 2)),
        Credito("002", "C2", 90.0, 1, date(2026, 6, 2)),
    ]
    _, filas = servicio.asignar(creditos, date(2026, 6, 2))
    assert all(f.reasignado for f in filas)
    assert [f.codigo_asesor for f in filas] == ["A", "B"]


def test_reproceso_conserva_cortes_anteriores_del_mes():
    """Al re-procesar el corte del día 4, conserva lo asignado el día 2 y
    recalcula como nuevas solo las propias del día 4."""
    servicio = AsignacionCarteraService(
        asesores_rotacion=_RotacionFija([("A", "Asesor A"), ("B", "Asesor B")]),
        asignacion_mensual=_MesPorFecha(
            {
                date(2026, 6, 2): {"001": ("Z", "Día 2")},
                date(2026, 6, 4): {"002": ("Z", "Día 4 previo")},
            },
        ),
    )
    creditos = [
        Credito("001", "C1", 100.0, 1, date(2026, 6, 4)),
        Credito("002", "C2", 90.0, 1, date(2026, 6, 4)),
    ]
    _, filas = servicio.asignar(creditos, date(2026, 6, 4))
    assert filas[0].codigo_asesor == "Z"
    assert filas[0].reasignado is False
    assert filas[1].reasignado is True


def test_falla_si_no_hay_asesores_activos_en_bd():
    import pytest

    servicio = AsignacionCarteraService(asesores_rotacion=_RotacionFija([]))
    with pytest.raises(ValueError, match="asesores activos"):
        servicio.asignar([Credito("001", "C", 100.0, 3, date(2026, 6, 2))], date(2026, 6, 2))
