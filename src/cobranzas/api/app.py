from fastapi import FastAPI, HTTPException

from cobranzas.api.schemas import (
    EjecutarPipelineRequest,
    FinMesRunResponse,
    LisExcelRunResponse,
    PipelineRunResponse,
)
from cobranzas.jobs.fin_mes_runner import ejecutar_fin_mes
from cobranzas.jobs.lis_excel_runner import ejecutar_lis_a_excel
from cobranzas.jobs.pipeline_runner import ejecutar_pipeline

app = FastAPI(
    title="Cobranzas — Mora Temprana",
    description=(
        "Ejecuta el pipeline diario (asesores, feriados, limpieza, asignación, BD).\n\n"
        "**Probar en Swagger:** `POST /pipeline` → Try it out → body "
        '`{"fecha": "05052026"}` → Execute.\n\n'
        "**Fin de mes (sin asignación):** `POST /acumulado-fin-mes` con la fecha "
        "del archivo; genera `acumulado_fin_mes_{MMDDYYYY}.xlsx` en destino/{año}/{MM}/ "
        "con columna FECHA DEL PROCESO = día hábil siguiente.\n\n"
        "**Convertir .lis a Excel:** `POST /lis-a-excel` con la fecha del lote; "
        "genera un `.xlsx` por archivo (camorosico y cadetacaco) en "
        "`destino/excel_lis/`.\n\n"
        "La fecha define la carpeta `docsmora/{año}/{MMDDYYYY}/cartera{MMDDYYYY}b/` "
        "(mes-día-año, ej. 05052026)."
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
    `docsmora/{año}/{MMDDYYYY}/cartera{MMDDYYYY}b/`
  """
    try:
        resultado = ejecutar_pipeline(
            fecha_corte=body.fecha,
            configurar_logs=True,
            es_fin_de_mes=body.es_fin_de_mes,
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


@app.post(
    "/lis-a-excel",
    response_model=LisExcelRunResponse,
    summary="Convertir los .lis del lote a Excel",
    tags=["Utilidades"],
)
def convertir_lis_a_excel_api(body: EjecutarPipelineRequest) -> dict:
    """
    Convierte camorosico + cadetacaco del lote indicado a `.xlsx` (un Excel por
    archivo) en `destino/excel_lis/`. Conversión fiel: una fila por línea, valores
    como texto (preserva ceros a la izquierda). No limpia ni fusiona.
    """
    try:
        resultado = ejecutar_lis_a_excel(fecha=body.fecha, configurar_logs=True)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    payload = resultado.to_dict()
    if not resultado.ok:
        raise HTTPException(status_code=404, detail=payload)
    return payload


@app.post(
    "/acumulado-fin-mes",
    response_model=FinMesRunResponse,
    summary="Limpieza + merge sin asignación → acumulado fin mes",
    tags=["Fin de mes"],
)
def ejecutar_acumulado_fin_mes_api(body: EjecutarPipelineRequest) -> dict:
    """
    Lee camorosico + cadetacaco (+ Recblue), limpia detalles, fusiona y escribe
    `destino/{año}/{MM}/acumulado_fin_mes_{MMDDYYYY}.xlsx` sin asignación ni BD.
    """
    try:
        resultado = ejecutar_fin_mes(
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
