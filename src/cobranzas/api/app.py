from fastapi import FastAPI, HTTPException

from cobranzas.api.schemas import EjecutarPipelineRequest, PipelineRunResponse
from cobranzas.jobs.pipeline_runner import ejecutar_pipeline

app = FastAPI(
    title="Cobranzas — Mora Temprana",
    description=(
        "Ejecuta el pipeline diario (asesores, feriados, limpieza, asignación, BD).\n\n"
        "**Probar en Swagger:** `POST /pipeline` → Try it out → body "
        '`{"fecha": "05042026"}` → Execute.\n\n'
        "La fecha define la carpeta `docsmora/{año}/{DDMMYYYY}/cartera{DDMMYYYY}b/`."
    ),
    version="0.1.0",
)


@app.get("/health", tags=["Sistema"])
def health() -> dict:
    return {"status": "ok"}


@app.post(
    "/pipeline",
    response_model=PipelineRunResponse,
    summary="Ejecutar pipeline diario",
    tags=["Pipeline"],
)
def ejecutar_pipeline_api(body: EjecutarPipelineRequest) -> dict:
    """
    Ejecuta Jobs 0 + 0b + 1 para la **fecha de corte** indicada.

    Busca archivos en:
    `docsmora/{año}/{DDMMYYYY}/cartera{DDMMYYYY}b/`
  """
    try:
        resultado = ejecutar_pipeline(
            fecha_corte=body.fecha,
            configurar_logs=True,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    payload = resultado.to_dict()
    if not resultado.ok:
        raise HTTPException(status_code=500, detail=payload)
    return payload
