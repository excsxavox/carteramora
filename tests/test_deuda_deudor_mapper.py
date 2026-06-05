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
        estado_operacion="RESOLUCION",
        nombre_oficial="LADY JOHANNA GONZALEZ VELASQUEZ",
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
            ("saldo_14_0x", "0.00"),
            ("saldo_14_1x", "1325.75"),
            ("saldo_14_2x", "486.31"),
            ("interes_normal", "106.08"),
            ("int_devengado", "0.00"),
            ("int_vencido", "81.03"),
            ("total_op", "1969.46"),
            ("est", "RESOLUCION"),
            ("dias_mora", "135"),
            ("decision", "Aprobado"),
            ("segmentacion", "A"),
            ("score", "705"),
        ),
    )
    deudor = mapear_deudor(credito)
    deuda = mapear_deuda(credito)

    assert deudor.documento == "1900299288"
    assert deudor.socio == "83736"
    assert deudor.nombre == "MINGA SALINAS MANUEL FRANCISCO"

    assert deuda.numero_operacion == "0015219214"
    assert deuda.fecha_corte == date(2026, 3, 6)
    assert deuda.cedula == "1900299288"
    assert deuda.socio == "83736"
    assert deuda.oficina == "1"
    assert deuda.desc_oficina == "CAYAMBE"
    assert deuda.sector == "P"
    assert deuda.tipo_operacion == "CONSUMO23"
    assert deuda.tipo_destino == "OT"
    assert float(deuda.valor_original_prestamo) == 5100.00
    assert float(deuda.saldo_capital_prestamo) == 1812.06
    assert deuda.calificacion == "E"
    assert float(deuda.total_provision) == 1812.06
    assert float(deuda.saldo_141x) == 1325.75
    assert float(deuda.total_operacion) == 1969.46
    assert deuda.estado == "RESOLUCION"
    assert deuda.dias_mora == 136
    assert deuda.oficial == "LADY JOHANNA GONZALEZ VELASQUEZ"
    assert deuda.decision == "Aprobado"
