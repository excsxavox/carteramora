"""Fin de mes: sin asignación de asesor, estado FIN_DE_MES y exclusión del día siguiente."""

from datetime import date
from unittest.mock import MagicMock

from sqlalchemy import create_engine, select

from cobranzas.application.chain.asignacion_handler import AsignacionHandler
from cobranzas.application.chain.exclusion_fin_mes_handler import ExclusionFinMesHandler
from cobranzas.application.chain.export_asignacion_handler import ExportAsignacionHandler
from cobranzas.application.chain.proceso_context import ProcesoContext
from cobranzas.domain.models.credito import Credito
from cobranzas.domain.services.asignacion_cartera_service import AsignacionCarteraService
from cobranzas.infrastructure.persistence.base import Base
from cobranzas.infrastructure.persistence.mappers.cobranza_credito_mapper import (
    ESTADO_ASESOR_FIN_DE_MES,
)
from cobranzas.infrastructure.persistence.models import AsesorDeuda
from cobranzas.infrastructure.persistence.repositories.acumulado_mensual_repository import (
    SqlAlchemyAcumuladoMensualRepository,
)
from cobranzas.infrastructure.persistence.repositories.cobranza_repository import (
    SqlAlchemyCobranzaRepository,
)
from cobranzas.infrastructure.persistence.session import get_session_factory


def _credito(operacion: str, fecha: date, dias: int = 5) -> Credito:
    return Credito(
        id_credito=operacion,
        cliente="CLIENTE",
        saldo_pendiente=100.0,
        dias_mora=dias,
        fecha_corte=fecha,
        codigo_oficial="520",
        estado_operacion="VIGENTE",
    )


def _session_factory():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return get_session_factory(engine)


def test_asignacion_servicio_no_rota_en_fin_de_mes():
    servicio = AsignacionCarteraService(asesores_rotacion=MagicMock())
    creditos = [_credito("001", date(2026, 5, 29))]

    resultado, filas = servicio.asignar(
        creditos, date(2026, 5, 29), es_fin_de_mes=True
    )

    assert filas == []
    assert resultado == creditos


def test_persistencia_fin_de_mes_estado_fin_de_mes_sin_asesor():
    session_factory = _session_factory()
    repo = SqlAlchemyCobranzaRepository(
        session_factory, usar_mora_temprana=True, es_fin_de_mes=True
    )

    repo.guardar_creditos_mora([_credito("001", date(2026, 5, 29))])

    with session_factory() as session:
        fila = session.scalar(select(AsesorDeuda))
    assert fila is not None
    assert fila.estado == ESTADO_ASESOR_FIN_DE_MES
    assert fila.id_asesor is None


def test_acumulado_incluye_fin_de_mes_con_asesor_en_blanco():
    session_factory = _session_factory()
    repo = SqlAlchemyCobranzaRepository(
        session_factory, usar_mora_temprana=True, es_fin_de_mes=True
    )
    fecha = date(2026, 5, 29)
    repo.guardar_creditos_mora([_credito("001", fecha)])

    filas = SqlAlchemyAcumuladoMensualRepository(session_factory).filas_por_fecha_corte(
        fecha
    )

    assert len(filas) == 1
    assert filas[0].operacion == "001"
    assert filas[0].estado_mora == ESTADO_ASESOR_FIN_DE_MES
    assert filas[0].usuario_asesor == ""
    assert filas[0].nombre_asesor == ""


def test_operaciones_fin_de_mes_devuelve_marcadas_de_corte_anterior():
    session_factory = _session_factory()
    repo_fdm = SqlAlchemyCobranzaRepository(
        session_factory, usar_mora_temprana=True, es_fin_de_mes=True
    )
    repo_fdm.guardar_creditos_mora([_credito("001", date(2026, 5, 29))])

    repo = SqlAlchemyCobranzaRepository(session_factory, usar_mora_temprana=True)
    operaciones = repo.operaciones_fin_de_mes(date(2026, 6, 1))

    assert operaciones == {"001"}
    # El mismo corte no se incluye a sí mismo.
    assert repo.operaciones_fin_de_mes(date(2026, 5, 29)) == set()


def test_exclusion_handler_quita_operaciones_de_fin_de_mes():
    puerto = MagicMock()
    puerto.operaciones_fin_de_mes.return_value = {"001"}
    handler = ExclusionFinMesHandler(puerto)
    contexto = ProcesoContext(dias_mora_minimo=1, usar_mora_temprana=True)
    contexto.es_fin_de_mes = False
    contexto.creditos = [
        _credito("001", date(2026, 6, 1)),
        _credito("002", date(2026, 6, 1)),
    ]

    resultado = handler._procesar(contexto)

    operaciones = {c.id_credito for c in resultado.creditos}
    assert operaciones == {"002"}
    puerto.operaciones_fin_de_mes.assert_called_once_with(date(2026, 6, 1))


def test_exclusion_handler_no_aplica_en_fin_de_mes():
    puerto = MagicMock()
    handler = ExclusionFinMesHandler(puerto)
    contexto = ProcesoContext(dias_mora_minimo=1, usar_mora_temprana=True)
    contexto.es_fin_de_mes = True
    contexto.creditos = [_credito("001", date(2026, 5, 29))]

    resultado = handler._procesar(contexto)

    assert len(resultado.creditos) == 1
    puerto.operaciones_fin_de_mes.assert_not_called()


def test_export_asignacion_omitido_en_fin_de_mes():
    export = MagicMock()
    handler = ExportAsignacionHandler(export)
    contexto = ProcesoContext(dias_mora_minimo=1, usar_mora_temprana=True)
    contexto.es_fin_de_mes = True
    contexto.creditos = [_credito("001", date(2026, 5, 29))]

    handler._procesar(contexto)

    export.exportar_csv.assert_not_called()
