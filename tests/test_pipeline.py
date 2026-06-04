from cobranzas.jobs import pipeline_runner


def test_pipeline_detiene_si_falla_sync(monkeypatch):
    monkeypatch.setattr(pipeline_runner, "job_sync_asesores", lambda: 1)
    llamadas = {"limpieza": 0}
    monkeypatch.setattr(
        pipeline_runner, "job_limpieza", lambda: llamadas.__setitem__("limpieza", 1) or 0
    )
    assert pipeline_runner.main() == 1
    assert llamadas["limpieza"] == 0


def test_pipeline_ejecuta_ambos_si_ok(monkeypatch):
    orden = []
    monkeypatch.setattr(
        pipeline_runner, "job_sync_asesores", lambda: orden.append("sync") or 0
    )
    monkeypatch.setattr(
        pipeline_runner, "job_limpieza", lambda: orden.append("limpieza") or 0
    )
    assert pipeline_runner.main() == 0
    assert orden == ["sync", "limpieza"]
