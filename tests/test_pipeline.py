from unittest.mock import MagicMock, patch

from cobranzas.application.chain.pipeline import PipelineContext
from cobranzas.infrastructure.config.settings import Settings
from cobranzas.jobs import pipeline_runner
from tests.conftest import RUTAS_MANUALES_FIXTURE


def test_pipeline_main_retorna_codigo_contexto(monkeypatch):
    settings = Settings(**RUTAS_MANUALES_FIXTURE)
    contexto = PipelineContext(settings=settings, codigo_salida=0)

    mock_chain = MagicMock()
    mock_chain.manejar.return_value = contexto
    monkeypatch.setattr(
        pipeline_runner,
        "build_settings",
        lambda fecha=None, es_fin_de_mes=None: settings,
    )
    monkeypatch.setattr(pipeline_runner, "_configure_logging", lambda _l: None)
    monkeypatch.setattr(pipeline_runner, "_preparar_base_datos", lambda _s: None)
    monkeypatch.setattr(pipeline_runner, "build_pipeline_chain", lambda: mock_chain)

    assert pipeline_runner.main() == 0
    mock_chain.manejar.assert_called_once()
