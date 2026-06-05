import logging

from cobranzas.application.chain.handler import Handler
from cobranzas.application.chain.proceso_context import ProcesoContext
from cobranzas.domain.ports.feriados_calendario_port import FeriadosCalendarioPort
from cobranzas.domain.services.mora_temprana_service import MoraTempranaService
from cobranzas.domain.services.resolver_reglas_mora_service import (
    ResolverReglasMoraService,
)

logger = logging.getLogger(__name__)


class MoraTempranaHandler(Handler):
    """Paso 3: filtros HU-GRC-01, días hábiles y orden por saldo capital."""

    def __init__(
        self,
        mora_temprana_service: MoraTempranaService,
        feriados_repository: FeriadosCalendarioPort,
        reglas_resolver: ResolverReglasMoraService,
    ) -> None:
        super().__init__()
        self._service = mora_temprana_service
        self._feriados = feriados_repository
        self._reglas = reglas_resolver

    def _procesar(self, contexto: ProcesoContext) -> ProcesoContext:
        if not contexto.usar_mora_temprana:
            return contexto

        feriados = self._feriados.fechas_vigentes()
        config = self._reglas.resolver(
            dias_min=contexto.mora_temprana_dias_min,
            dias_max=contexto.mora_temprana_dias_max,
            estados_excluidos=contexto.estados_excluidos,
            tipos_oper_excluidos=contexto.tipos_oper_excluidos,
        )
        creditos, metricas = self._service.procesar(
            contexto.creditos,
            feriados=feriados,
            dias_min=config.dias_min,
            dias_max=config.dias_max,
            estados_excluidos=config.estados_excluidos,
            tipos_oper_excluidos=config.tipos_oper_excluidos,
            usar_calculo_dia_pago=True,
        )
        metricas["reglas_origen"] = config.origen
        contexto.creditos = creditos
        contexto.metricas_mora_temprana = metricas
        logger.info("Mora temprana aplicada | elegibles=%s", len(creditos))
        return contexto
