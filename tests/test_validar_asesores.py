import pytest

from cobranzas.domain.models.asesor_registro import AsesorRegistro
from cobranzas.domain.services.validar_asesores_service import (
    ValidacionAsesoresError,
    validar_registros_asesores,
)


def test_rechaza_cedula_duplicada_en_excel():
    registros = [
        AsesorRegistro("OF-87", "A", email="a@test.com"),
        AsesorRegistro("OF-87", "B", email="b@test.com"),
    ]
    with pytest.raises(ValidacionAsesoresError, match="duplicada"):
        validar_registros_asesores(registros, rechazar_duplicados_excel=True)


def test_deduplica_si_no_rechazar():
    registros = [
        AsesorRegistro("OF-87", "PRIMERO"),
        AsesorRegistro("OF-87", "SEGUNDO"),
    ]
    unicos, advertencias = validar_registros_asesores(
        registros, rechazar_duplicados_excel=False
    )
    assert len(unicos) == 1
    assert unicos[0].nombre == "SEGUNDO"
    assert any("duplicada" in a.lower() for a in advertencias)


def test_rechaza_email_invalido():
    with pytest.raises(ValidacionAsesoresError, match="email"):
        validar_registros_asesores(
            [AsesorRegistro("OF-1", "NOMBRE VALIDO", email="no-es-email")],
        )
