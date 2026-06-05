from unittest.mock import patch

import pytest

from cobranzas.domain.models.pipeline_run_result import PipelineRunResult
from cobranzas.infrastructure.config.fecha_corte import normalizar_fecha_corte

fastapi = pytest.importorskip("fastapi")
httpx = pytest.importorskip("httpx")
from fastapi.testclient import TestClient  # noqa: E402

from cobranzas.api.app import app  # noqa: E402


def test_normalizar_fecha_iso():
    assert normalizar_fecha_corte("2026-05-05") == "05052026"


def test_normalizar_fecha_mmddyyyy():
    assert normalizar_fecha_corte("05052026") == "05052026"


@patch("cobranzas.api.app.ejecutar_pipeline")
def test_post_pipeline_ok(mock_ejecutar):
    mock_ejecutar.return_value = PipelineRunResult(
        ok=True,
        codigo_salida=0,
        fecha_corte="05052026",
        archivo_morosidad="docsmora/2026/05042026/cartera05042026b/camorosico.lis",
        archivo_cartera="docsmora/2026/05042026/cartera05042026b/cadetacaco.lis",
        archivo_salida_morosidad="destino/2026/05042026/cartera05042026b/detalle_morosidad.lis",
        archivo_salida_mora="destino/2026/05042026/cartera05042026b/reporte_mora.lis",
        archivo_asignacion="destino/2026/05042026/cartera05042026b/ASIGNACION.csv",
        total_en_mora=100,
        total_saldo_mora=5000.0,
        registros_persistidos_bd=100,
        asignaciones_generadas=100,
    )

    client = TestClient(app)
    response = client.post("/pipeline", json={"fecha": "2026-05-05"})

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["fecha_corte"] == "05052026"
    mock_ejecutar.assert_called_once_with(
        fecha_corte="05052026",
        configurar_logs=True,
    )


@patch("cobranzas.api.app.ejecutar_pipeline")
def test_post_pipeline_archivo_no_encontrado(mock_ejecutar):
    mock_ejecutar.side_effect = FileNotFoundError("No existe carpeta de lote")

    client = TestClient(app)
    response = client.post("/pipeline", json={"fecha": "05062026"})

    assert response.status_code == 404


def test_health():
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}
