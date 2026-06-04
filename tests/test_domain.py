from datetime import date

from cartera_mora.domain.models.credito import Credito, EstadoMora
from cartera_mora.domain.services.cartera_mora_service import CarteraMoraService


def _credito(dias_mora: int) -> Credito:
    return Credito(
        id_credito="CR-TEST",
        cliente="Test",
        saldo_pendiente=1000.0,
        dias_mora=dias_mora,
        fecha_corte=date(2026, 6, 1),
    )


def test_clasificar_al_dia():
    assert _credito(10).clasificar_mora(30) == EstadoMora.AL_DIA


def test_clasificar_mora_leve():
    assert _credito(45).clasificar_mora(30) == EstadoMora.MORA_LEVE


def test_clasificar_mora_grave():
    assert _credito(120).clasificar_mora(30) == EstadoMora.MORA_GRAVE


def test_filtrar_en_mora():
    service = CarteraMoraService()
    creditos = [_credito(10), _credito(45), _credito(120)]
    en_mora = service.filtrar_en_mora(creditos, dias_mora_minimo=30)
    assert len(en_mora) == 2


def test_construir_reporte_totales():
    service = CarteraMoraService()
    creditos = [_credito(45), _credito(120)]
    reporte = service.construir_reporte(creditos, dias_mora_minimo=30)
    assert reporte["total_creditos"] == 2
    assert reporte["total_saldo_mora"] == 2000.0
    assert len(reporte["mora_leve"]) == 1
    assert len(reporte["mora_grave"]) == 1
