from datetime import date

from cobranzas.domain.models.credito import Credito
from cobranzas.infrastructure.persistence.mappers.deuda_deudor_mapper import (
    mapear_deuda,
    mapear_deudor,
)


def test_mapear_deudor_y_deuda_desde_campos_tab():
    credito = Credito(
        "0015219214",
        "MINGA SALINAS MANUEL FRANCISCO",
        611.30,
        136,
        date(2026, 3, 6),
        cedula="1900299288",
        socio="83736",
        calificacion="E",
        campos_tab=(
            ("oficina", "1"),
            ("desc_oficina", "CAYAMBE"),
            ("sector", "P"),
            ("tipo_oper", "CONSUMO23"),
            ("tipo_dest", "OT"),
            ("fecha_de_concesion", "02/17/2023"),
            ("fecha_de_vencimiento", "02/17/2027"),
            ("fecha_ultimo_pago", "01/05/2026"),
            ("valor_ori_prestam", "5100.00"),
            ("saldo_cap_prest", "1812.06"),
            ("calificac", "E"),
            ("total_provision", "1812.06"),
        ),
    )
    deudor = mapear_deudor(credito)
    deuda = mapear_deuda(credito)

    assert deudor.documento == "1900299288"
    assert deudor.socio == "83736"
    assert deudor.nombre == "MINGA SALINAS MANUEL FRANCISCO"

    assert deuda.numero_operacion == "0015219214"
    assert deuda.oficina == "1"
    assert deuda.descripcion_oficina == "CAYAMBE"
    assert deuda.sector == "P"
    assert deuda.tipo_operacion == "CONSUMO23"
    assert deuda.tipo_destino == "OT"
    assert float(deuda.valor_original_prestamo) == 5100.00
    assert float(deuda.saldo_capital_prestamo) == 1812.06
    assert deuda.calificacion == "E"
    assert float(deuda.total_provision) == 1812.06
