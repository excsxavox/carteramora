from datetime import date

from cobranzas.domain.models.credito import Credito
from cobranzas.domain.services.asignacion_cartera_service import AsignacionCarteraService
from cobranzas.infrastructure.config.settings import Settings
from cobranzas.infrastructure.persistence.database import (
    create_engine_from_settings,
    init_database,
)
from cobranzas.infrastructure.persistence.repositories import SqlAlchemyCobranzaRepository
from cobranzas.infrastructure.persistence.repositories.asignacion_mensual_repository import (
    SqlAlchemyAsignacionMensualRepository,
)
from cobranzas.infrastructure.persistence.repositories.asesores_rotacion_repository import (
    SqlAlchemyAsesoresRotacionRepository,
)
from cobranzas.infrastructure.persistence.session import get_session_factory
from cobranzas.infrastructure.persistence.models import Asesor


def _credito_temprana(
    operacion: str,
    fecha: date,
    codigo: str,
    nombre: str,
) -> Credito:
    return Credito(
        operacion,
        "CLIENTE",
        1000.0,
        2,
        fecha,
        cedula="1234567890",
        codigo_oficial=codigo,
        nombre_oficial=nombre,
        campos_tab=(("saldo_cap_prest", "1000"), ("dia_pago", "2")),
    )


def _setup_bd(tmp_path):
    db_path = tmp_path / "asignacion.sqlite"
    engine = create_engine_from_settings(
        Settings(DATABASE_URL=f"sqlite:///{db_path.as_posix()}")
    )
    init_database(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        session.add(
            Asesor(nombre="Asesor A", cedula="OF-A", activo=True)
        )
        session.add(
            Asesor(nombre="Asesor B", cedula="OF-B", activo=True)
        )
        session.commit()
    return factory


def test_asignaciones_del_mes_lee_corte_dia_posterior(tmp_path):
    factory = _setup_bd(tmp_path)
    repo = SqlAlchemyCobranzaRepository(
        factory,
        dias_mora_minimo=1,
        usar_mora_temprana=True,
        mora_temprana_dias_min=1,
        mora_temprana_dias_max=0,
    )
    repo.guardar_creditos_mora(
        [
            _credito_temprana("001", date(2026, 6, 5), "A", "Asesor A"),
            _credito_temprana("002", date(2026, 6, 5), "B", "Asesor B"),
        ]
    )

    mensual = SqlAlchemyAsignacionMensualRepository(factory)
    asignadas = mensual.asignaciones_del_mes(2026, 6)

    assert asignadas == {
        "001": ("A", "Asesor A"),
        "002": ("B", "Asesor B"),
    }


def test_dia_4_tras_dia_5_persistido_cero_nuevas(tmp_path):
    factory = _setup_bd(tmp_path)
    cobranza = SqlAlchemyCobranzaRepository(
        factory,
        dias_mora_minimo=1,
        usar_mora_temprana=True,
        mora_temprana_dias_min=1,
        mora_temprana_dias_max=0,
    )
    cobranza.guardar_creditos_mora(
        [
            _credito_temprana("001", date(2026, 6, 5), "A", "Asesor A"),
            _credito_temprana("002", date(2026, 6, 5), "B", "Asesor B"),
        ]
    )

    servicio = AsignacionCarteraService(
        asesores_rotacion=SqlAlchemyAsesoresRotacionRepository(factory),
        asignacion_mensual=SqlAlchemyAsignacionMensualRepository(factory),
    )
    creditos = [
        _credito_temprana("001", date(2026, 6, 4), "", ""),
        _credito_temprana("002", date(2026, 6, 4), "", ""),
    ]
    _, filas = servicio.asignar(creditos, date(2026, 6, 4))

    assert sum(1 for f in filas if f.reasignado) == 0
    assert [f.codigo_asesor for f in filas] == ["A", "B"]
