"""Composition root: ensambla dependencias (inyección manual)."""

from typing import Optional, Tuple

from cobranzas.application.use_cases.procesar_cobranzas import (
    ProcesarCobranzasUseCase,
)
from cobranzas.domain.services.asignacion_cartera_service import AsignacionCarteraService
from cobranzas.domain.services.cobranzas_service import CobranzasService
from cobranzas.domain.services.cartera_merge_service import CarteraMergeService
from cobranzas.domain.services.persistir_cartera_mora_service import (
    PersistirCarteraMoraService,
)
from cobranzas.infrastructure.adapters.recblue_archivo_adapter import RecblueArchivoAdapter
from cobranzas.infrastructure.adapters.tsv_credito_repository import (
    TsvCreditoRepository,
)
from cobranzas.infrastructure.adapters.tsv_cartera_repository import (
    TsvCarteraRepository,
)
from cobranzas.infrastructure.config.database_url import resolver_database_url
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
from cobranzas.domain.services.resolver_reglas_mora_service import (
    ResolverReglasMoraService,
)
from cobranzas.domain.services.sembrar_reglas_mora_service import SembrarReglasMoraService
from cobranzas.infrastructure.persistence.repositories.feriados_calendario_repository import (
    SqlAlchemyFeriadosCalendarioRepository,
)
from cobranzas.infrastructure.persistence.repositories.reglas_repository import (
    SqlAlchemyReglasRepository,
)
from cobranzas.infrastructure.persistence.session import get_session_factory


def _lista_csv(texto: str) -> Tuple[str, ...]:
    return tuple(p.strip() for p in (texto or "").split(",") if p.strip())


def build_procesar_cobranzas_use_case(
    settings: Optional[Settings] = None,
) -> ProcesarCobranzasUseCase:
    cfg = settings or Settings()
    persistir_service: Optional[PersistirCarteraMoraService] = None
    feriados_repo = None
    reglas_resolver = None
    asignacion_service = None
    recblue_adapter = None
    session_factory = None

    if cfg.archivo_recblue is not None:
        recblue_adapter = RecblueArchivoAdapter(cfg.archivo_recblue)

    if cfg.persistir_en_bd or cfg.usar_mora_temprana:
        engine = create_engine_from_settings(cfg)
        init_database(engine)
        session_factory = get_session_factory(engine)

    if cfg.persistir_en_bd and session_factory is not None:
        persistir_service = PersistirCarteraMoraService(
            SqlAlchemyCobranzaRepository(
                session_factory,
                cfg.dias_mora_minimo,
                recblue=recblue_adapter,
                usar_mora_temprana=cfg.usar_mora_temprana,
                mora_temprana_dias_min=cfg.mora_temprana_dias_min,
                mora_temprana_dias_max=cfg.mora_temprana_dias_max,
            ),
            dias_mora_minimo=cfg.dias_mora_minimo,
        )

    if cfg.usar_mora_temprana and session_factory is not None:
        reglas_repo = SqlAlchemyReglasRepository(session_factory)
        SembrarReglasMoraService(reglas_repo).sembrar_si_vacio(
            estados_excluidos=_lista_csv(cfg.estados_excluidos),
            tipos_oper_excluidos=_lista_csv(cfg.tipos_oper_excluidos),
            dias_min=cfg.mora_temprana_dias_min,
            dias_max=cfg.mora_temprana_dias_max,
        )
        reglas_resolver = ResolverReglasMoraService(
            reglas_repo, usar_reglas_bd=cfg.usar_reglas_bd
        )
        feriados_repo = SqlAlchemyFeriadosCalendarioRepository(
            session_factory, cfg.clave_feriados
        )
        asignacion_mensual = (
            SqlAlchemyAsignacionMensualRepository(session_factory)
            if cfg.persistir_en_bd
            else None
        )
        asignacion_service = AsignacionCarteraService(
            asesores_rotacion=SqlAlchemyAsesoresRotacionRepository(session_factory),
            asignacion_mensual=asignacion_mensual,
            recblue=recblue_adapter,
        )

    return ProcesarCobranzasUseCase.crear(
        morosidad_repository=TsvCreditoRepository(cfg.archivo_morosidad),
        cartera_repository=TsvCarteraRepository(cfg.archivo_cartera),
        cobranzas_service=CobranzasService(),
        cartera_merge_service=CarteraMergeService(),
        dias_mora_minimo=cfg.dias_mora_minimo,
        archivo_morosidad=cfg.archivo_morosidad,
        archivo_cartera=cfg.archivo_cartera,
        archivo_detalle_morosidad=cfg.archivo_salida_morosidad,
        archivo_detalle_mora=cfg.archivo_salida_mora,
        persistir_service=persistir_service,
        persistir_en_bd=cfg.persistir_en_bd,
        database_url=resolver_database_url(cfg),
        usar_mora_temprana=cfg.usar_mora_temprana,
        mora_temprana_dias_min=cfg.mora_temprana_dias_min,
        mora_temprana_dias_max=cfg.mora_temprana_dias_max,
        estados_excluidos=_lista_csv(cfg.estados_excluidos),
        tipos_oper_excluidos=_lista_csv(cfg.tipos_oper_excluidos),
        archivo_asignacion=cfg.archivo_salida_asignacion,
        feriados_repository=feriados_repo,
        reglas_resolver=reglas_resolver,
        asignacion_service=asignacion_service,
        recblue_adapter=recblue_adapter,
        archivo_recblue=cfg.archivo_recblue,
    )
