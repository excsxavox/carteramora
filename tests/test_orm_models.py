from cobranzas.infrastructure.persistence import Base
from cobranzas.infrastructure.persistence.models import (
    Asesor,
    AsesorDeuda,
    Catalogo,
    Clave,
    Deuda,
    Deudor,
    LogAuditoria,
    Regla,
)


def test_tablas_registradas_en_metadata():
    tablas = {t.name for t in Base.metadata.sorted_tables}
    assert tablas == {
        "asesores",
        "asesores_deuda",
        "catalogo",
        "claves",
        "deuda",
        "deudores",
        "logs_auditoria",
        "reglas",
        "tmp_columna_archivo",
        "tmp_lote_carga",
        "tmp_mapeo_columna",
        "tmp_stg_mora",
        "tmp_stg_morosidad",
    }


def test_deuda_relacion_con_deudor():
    assert Deuda.deudor.property.back_populates == "deudas"


def test_asesor_deuda_foreign_keys():
    fk_targets = {
        fk.target_fullname
        for fk in AsesorDeuda.__table__.foreign_keys
    }
    assert fk_targets == {"asesores.id_asesor", "deuda.id_deuda"}


def test_catalogo_foreign_key_clave():
    fk_targets = {fk.target_fullname for fk in Catalogo.__table__.foreign_keys}
    assert fk_targets == {"claves.id_clave"}


def test_columnas_pk():
    assert Asesor.id_asesor.primary_key
    assert Deudor.id_deudor.primary_key
    assert Deuda.id_deuda.primary_key
    assert Regla.id_regla.primary_key
    assert LogAuditoria.id_log.primary_key
