from datetime import date
from pathlib import Path

from cobranzas.domain.models.credito import Credito
from cobranzas.domain.services.manifiesto_lis_service import ManifiestoLisService


def test_manifiesto_contiene_leidos_y_generados(tmp_path: Path):
    creditos = [
        Credito("001", "Cliente A", 100.0, 45, date(2026, 3, 6), estado_operacion="VIGENTE"),
        Credito("002", "Cliente B", 50.0, 10, date(2026, 3, 6), estado_operacion="VIGENTE"),
    ]
    mora = [creditos[0]]
    reporte = {
        "fecha_corte": "2026-03-06",
        "dias_mora_minimo": 30,
        "total_creditos": 1,
        "total_saldo_mora": 100.0,
    }

    contenido = ManifiestoLisService().construir(
        archivo_morosidad=tmp_path / "morosidad.txt",
        archivo_cartera=tmp_path / "cartera.txt",
        archivo_reporte=tmp_path / "reporte.json",
        archivo_lis=tmp_path / "reporte.lis",
        creditos_morosidad=creditos,
        total_cartera_leidas=5,
        total_enriquecidos=1,
        creditos_mora=mora,
        reporte=reporte,
    )

    assert "ARCHIVOS LEIDOS" in contenido
    assert "ARCHIVOS GENERADOS" in contenido
    assert "morosidad.txt" in contenido
    assert "cartera.txt" in contenido
    assert "reporte.json" in contenido
    assert "reporte.lis" in contenido
    assert "DETALLE LEIDO" in contenido
    assert "DETALLE GENERADO" in contenido
    assert "001\tCliente A" in contenido
    assert "CUADRO DE MOROSIDAD" in contenido
    assert "TE DETALLADO DE CARTERA" in contenido
