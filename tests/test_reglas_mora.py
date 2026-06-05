from datetime import date
from typing import List, Optional

from cobranzas.domain.constants.regla_tipo import (
    EXCLUSION_ESTADO,
    EXCLUSION_TIPO_OPER,
    MORA_TEMPRANA_DIAS_MAX,
    MORA_TEMPRANA_DIAS_MIN,
)
from cobranzas.domain.models.credito import Credito
from cobranzas.domain.ports.reglas_repository_port import ReglaNegocio, ReglasRepositoryPort
from cobranzas.domain.services.mora_temprana_service import (
    MoraTempranaService,
    debe_excluir_operacion,
)
from cobranzas.domain.services.resolver_reglas_mora_service import ResolverReglasMoraService
from cobranzas.domain.services.sembrar_reglas_mora_service import SembrarReglasMoraService
from cobranzas.infrastructure.config.settings import Settings
from cobranzas.infrastructure.persistence.database import (
    create_engine_from_settings,
    init_database,
)
from cobranzas.infrastructure.persistence.repositories.reglas_repository import (
    SqlAlchemyReglasRepository,
)
from cobranzas.infrastructure.persistence.session import get_session_factory


class _ReglasMemoria(ReglasRepositoryPort):
    def __init__(self, reglas: Optional[List[ReglaNegocio]] = None) -> None:
        self._reglas = list(reglas or [])
        self._id = 1

    def contar_reglas(self) -> int:
        return len(self._reglas)

    def listar_activas_por_tipos(self, tipos):
        return [r for r in self._reglas if r.tipo in tipos]

    def insertar_reglas(self, reglas):
        self._reglas.extend(reglas)
        return len(reglas)


def test_resolver_usa_reglas_bd():
    repo = _ReglasMemoria(
        [
            ReglaNegocio(EXCLUSION_ESTADO, "CASTIGADO"),
            ReglaNegocio(EXCLUSION_TIPO_OPER, "COMPRA CARTERA"),
            ReglaNegocio(MORA_TEMPRANA_DIAS_MIN, "2"),
            ReglaNegocio(MORA_TEMPRANA_DIAS_MAX, "28"),
        ]
    )
    config = ResolverReglasMoraService(repo).resolver(
        dias_min=1,
        dias_max=29,
        estados_excluidos=("OTRO",),
        tipos_oper_excluidos=(),
    )
    assert config.origen == "bd"
    assert config.dias_min == 2
    assert config.dias_max == 28
    assert config.estados_excluidos == ("CASTIGADO",)
    assert config.tipos_oper_excluidos == ("COMPRA CARTERA",)


def test_resolver_fallback_env_si_bd_vacia():
    repo = _ReglasMemoria()
    config = ResolverReglasMoraService(repo).resolver(
        dias_min=1,
        dias_max=29,
        estados_excluidos=("JUDICIAL",),
        tipos_oper_excluidos=(),
    )
    assert config.origen == "env"
    assert config.estados_excluidos == ("JUDICIAL",)


def test_excluye_judicial_con_regla_bd(tmp_path):
    credito = Credito(
        "001",
        "CLIENTE",
        100.0,
        5,
        date(2026, 6, 2),
        estado_operacion="GESTION JUDICIAL",
        campos_tab=(("dia_pago", "1"),),
    )
    excluir, _ = debe_excluir_operacion(credito, ("GESTION JUDICIAL",), ())
    assert excluir

    servicio = MoraTempranaService()
    elegibles, _ = servicio.procesar(
        [credito],
        feriados=set(),
        dias_min=1,
        dias_max=29,
        estados_excluidos=("GESTION JUDICIAL",),
        tipos_oper_excluidos=(),
    )
    assert len(elegibles) == 0


def test_sembrar_reglas_sqlite(tmp_path):
    db_path = tmp_path / "reglas.sqlite"
    engine = create_engine_from_settings(
        Settings(DATABASE_URL=f"sqlite:///{db_path.as_posix()}")
    )
    init_database(engine)
    repo = SqlAlchemyReglasRepository(get_session_factory(engine))
    assert repo.contar_reglas() == 0
    insertadas = SembrarReglasMoraService(repo).sembrar_si_vacio()
    assert insertadas == 7
    assert repo.contar_reglas() == 7
    assert SembrarReglasMoraService(repo).sembrar_si_vacio() == 0
