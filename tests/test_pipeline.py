from unittest.mock import MagicMock, patch

from cobranzas.application.chain.pipeline import PipelineContext
from cobranzas.infrastructure.config.settings import Settings
from cobranzas.jobs import pipeline_runner


def test_pipeline_main_retorna_codigo_contexto(monkeypatch):
    settings = Settings()
    contexto = PipelineContext(settings=settings, codigo_salida=0)

    mock_chain = MagicMock()
    mock_chain.manejar.return_value = contexto
    monkeypatch.setattr(pipeline_runner, "Settings", lambda: settings)
    monkeypatch.setattr(pipeline_runner, "_configure_logging", lambda _l: None)
    monkeypatch.setattr(pipeline_runner, "build_pipeline_chain", lambda: mock_chain)

    assert pipeline_runner.main() == 0
    mock_chain.manejar.assert_called_once()
