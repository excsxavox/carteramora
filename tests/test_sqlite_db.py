from datetime import date
from pathlib import Path

from cobranzas.domain.models.credito import Credito
from cobranzas.infrastructure.config.settings import Settings
from cobranzas.infrastructure.persistence import Base
from cobranzas.infrastructure.persistence.database import (
    create_engine_from_settings,
    init_database,
    verificar_conexion,
)
from cobranzas.infrastructure.persistence.repositories import SqlAlchemyCobranzaRepository
from cobranzas.infrastructure.persistence.session import get_session_factory
from cobranzas.infrastructure.persistence.mappers.cobranza_credito_mapper import (
    CLAVE_CLASIFICACION_MORA,
    PREFIJO_CEDULA_ASESOR,
)
from cobranzas.infrastructure.persistence.models import (
    Asesor,
    AsesorDeuda,
    Catalogo,
    Clave,
    Deuda,
    Deudor,
)


def test_init_sqlite_crea_tablas(tmp_path: Path):
    db_path = tmp_path / "test.sqlite"
    settings = Settings(
        DATABASE_URL=f"sqlite:///{db_path.as_posix()}",
        PERSISTIR_EN_BD=True,
    )
    engine = create_engine_from_settings(settings)
    init_database(engine)
    assert verificar_conexion(engine)
    assert {t.name for t in Base.metadata.sorted_tables} == {
        "asesores",
        "asesores_deuda",
        "catalogo",
        "claves",
        "deuda",
        "deudores",
        "logs_auditoria",
        "reglas",
        "tmp_columna_archivo",
        "tmp_lote_carga",
        "tmp_mapeo_columna",
        "tmp_stg_mora",
        "tmp_stg_morosidad",
    }


def test_persistir_credito_mora(tmp_path: Path):
    db_path = tmp_path / "cobranza.sqlite"
    engine = create_engine_from_settings(
        Settings(DATABASE_URL=f"sqlite:///{db_path.as_posix()}")
    )
    init_database(engine)
    repo = SqlAlchemyCobranzaRepository(get_session_factory(engine))
    credito = Credito(
        "0015219214",
        "CLIENTE PRUEBA",
        611.30,
        136,
        date(2026, 3, 6),
        cedula="1900299288",
        socio="83736",
        codigo_oficial="0047",
        nombre_oficial="OFICIAL COBRANZA",
        estado_operacion="VIGENTE",
        total_atrasado=1200.50,
        total_operacion=5000.00,
        campos_tab=(
            ("oficina", "1"),
            ("desc_oficina", "CAYAMBE"),
            ("sector", "P"),
            ("tipo_oper", "CONSUMO23"),
            ("tipo_dest", "OT"),
            ("fecha_de_concesion", "02/17/2023"),
            ("fecha_de_vencimiento", "02/17/2027"),
            ("fecha_ultimo_pago", "01/05/2026"),
            ("valor_ori_prestam", "5000.00"),
            ("saldo_cap_prest", "1812.06"),
            ("calificac", "E"),
            ("total_provision", "1812.06"),
        ),
    )
    assert repo.guardar_creditos_mora([credito]) == 1

    with get_session_factory(engine)() as session:
        deudor = session.query(Deudor).filter_by(documento="1900299288").one()
        deuda = session.query(Deuda).filter_by(numero_operacion="0015219214").one()
        assert deudor.nombre == "CLIENTE PRUEBA"
        assert deudor.socio == "83736"
        assert deuda.id_deudor == deudor.id_deudor
        assert deuda.oficina == "1"
        assert deuda.desc_oficina == "CAYAMBE"
        assert deuda.cedula == "1900299288"
        assert deuda.socio == "83736"
        assert deuda.tipo_operacion == "CONSUMO23"
        assert float(deuda.valor_original_prestamo) == 5000.00
        assert deuda.calificacion == "E"
        assert deuda.fecha_corte == date(2026, 3, 6)
        assert deuda.fecha_carga is not None

        asesor = session.query(Asesor).filter_by(
            cedula=f"{PREFIJO_CEDULA_ASESOR}0047"
        ).one()
        assert asesor.nombre == "OFICIAL COBRANZA"

        clave = session.query(Clave).filter_by(clave=CLAVE_CLASIFICACION_MORA).one()
        catalogo = (
            session.query(Catalogo)
            .filter_by(id_clave=clave.id_clave, valor="mora_grave")
            .one()
        )

        asignacion = session.query(AsesorDeuda).filter_by(id_deuda=deuda.id_deuda).one()
        assert asignacion.id_asesor == asesor.id_asesor
        assert asignacion.id_catalogo == catalogo.id_catalogo
        assert asignacion.estado == "VIGENTE"
        assert float(asignacion.monto) == 1200.50
        assert float(asignacion.monto_inicial) == 5000.00
        assert float(asignacion.monto_mora) == 611.30
        assert asignacion.fecha_asignacion == date(2026, 3, 6)
