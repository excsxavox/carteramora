import csv
from datetime import date
from pathlib import Path

from cobranzas.domain.models.asignacion_credito import AsignacionCredito
from cobranzas.domain.services.exportar_asignacion_service import ExportarAsignacionService


def test_export_asignacion_solo_id_credito_y_usuario(tmp_path: Path):
    ruta = tmp_path / "ASIGNACION.csv"
    filas = [
        AsignacionCredito(
            fecha_corte=date(2026, 5, 5),
            numero_operacion="0060058778",
            identificacion="0400671327",
            socio="123",
            nombre="CLIENTE UNO",
            saldo_capital=1000.0,
            dias_mora=10,
            codigo_asesor="LMANOSALVAS",
            nombre_asesor="LMANOSALVAS",
            id_credito_recblue="103102",
        ),
        AsignacionCredito(
            fecha_corte=date(2026, 5, 5),
            numero_operacion="0040092851",
            identificacion="1001118254",
            socio="456",
            nombre="CLIENTE DOS",
            saldo_capital=500.0,
            dias_mora=5,
            codigo_asesor="EGUERRA",
            nombre_asesor="EGUERRA",
            id_credito_recblue="",
        ),
    ]

    ExportarAsignacionService().exportar_csv(ruta, filas)

    with ruta.open(encoding="utf-8-sig", newline="") as fh:
        contenido = list(csv.DictReader(fh))

    assert list(contenido[0].keys()) == ["ID_CREDITO", "USUARIO"]
    assert contenido == [{"ID_CREDITO": "103102", "USUARIO": "LMANOSALVAS"}]


def test_export_usa_mapa_recblue_post_enriquecimiento(tmp_path: Path):
    ruta = tmp_path / "ASIGNACION.csv"
    filas = [
        AsignacionCredito(
            fecha_corte=date(2026, 5, 5),
            numero_operacion="0060058778",
            identificacion="x",
            socio="1",
            nombre="A",
            saldo_capital=1.0,
            dias_mora=1,
            codigo_asesor="MARCOS",
            nombre_asesor="MARCOS",
            id_credito_recblue="",
        ),
    ]
    mapa = {"0060058778": "97629"}

    ExportarAsignacionService().exportar_csv(ruta, filas, ids_recblue_por_operacion=mapa)

    with ruta.open(encoding="utf-8-sig", newline="") as fh:
        fila = next(csv.DictReader(fh))

    assert fila == {"ID_CREDITO": "97629", "USUARIO": "MARCOS"}
