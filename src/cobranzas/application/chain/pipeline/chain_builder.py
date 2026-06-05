from cobranzas.application.chain.pipeline.limpieza_handler import LimpiezaPipelineHandler
from cobranzas.application.chain.pipeline.staging_handler import StagingPipelineHandler
from cobranzas.application.chain.pipeline.pipeline_handler import PipelineHandler
from cobranzas.application.chain.pipeline.sync_asesores_handler import (
    SyncAsesoresPipelineHandler,
)
from cobranzas.application.chain.pipeline.sync_feriados_handler import (
    SyncFeriadosPipelineHandler,
)


def build_pipeline_chain() -> PipelineHandler:
    """Cadena: asesores → feriados → limpieza → [staging opcional]."""
    asesores = SyncAsesoresPipelineHandler()
    cadena = asesores.enlazar(SyncFeriadosPipelineHandler()).enlazar(
        LimpiezaPipelineHandler()
    )
    cadena.enlazar(StagingPipelineHandler())
    return asesores
