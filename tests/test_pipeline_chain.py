from unittest.mock import MagicMock, patch

from cobranzas.application.chain.pipeline import PipelineContext, build_pipeline_chain
from cobranzas.infrastructure.config.settings import Settings


def test_pipeline_detiene_si_fallan_asesores():
    settings = Settings()
    contexto = PipelineContext(settings=settings)

    with patch(
        "cobranzas.application.chain.pipeline.sync_asesores_handler.build_sincronizar_asesores_use_case"
    ) as mock_build:
        mock_build.return_value.ejecutar.side_effect = FileNotFoundError("sin excel")
        contexto = build_pipeline_chain().manejar(contexto)

    assert contexto.codigo_salida == 1
    assert contexto.detener is True


def test_pipeline_ejecuta_feriados_despues_de_asesores():
    settings = Settings()
    contexto = PipelineContext(settings=settings)
    orden: list[str] = []

    with patch(
        "cobranzas.application.chain.pipeline.sync_asesores_handler.build_sincronizar_asesores_use_case"
    ) as mock_asesores, patch(
        "cobranzas.application.chain.pipeline.sync_feriados_handler.build_sincronizar_feriados_use_case"
    ) as mock_feriados, patch(
        "cobranzas.application.chain.pipeline.limpieza_handler.build_procesar_cobranzas_use_case"
    ) as mock_limpieza:
        resultado_asesores = MagicMock()
        resultado_asesores.errores = []
        mock_asesores.return_value.ejecutar.return_value = resultado_asesores

        resultado_feriados = MagicMock()
        resultado_feriados.omitidos_sin_excel = False
        resultado_feriados.errores = []
        mock_feriados.return_value.ejecutar.side_effect = (
            lambda: orden.append("feriados") or resultado_feriados
        )

        resultado_limpieza = MagicMock()
        resultado_limpieza.total_creditos_procesados = 1
        resultado_limpieza.total_en_mora = 1
        resultado_limpieza.total_saldo_mora = 0.0
        resultado_limpieza.registros_persistidos_bd = 0
        mock_limpieza.return_value.ejecutar.side_effect = (
            lambda: orden.append("limpieza") or resultado_limpieza
        )
        mock_asesores.return_value.ejecutar.side_effect = (
            lambda: orden.append("asesores") or resultado_asesores
        )

        contexto = build_pipeline_chain().manejar(contexto)

    assert contexto.codigo_salida == 0
    assert orden == ["asesores", "feriados", "limpieza"]
