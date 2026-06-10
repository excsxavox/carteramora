"""Migraciones incrementales SQLite (columnas nuevas en BD existente)."""

import logging

from sqlalchemy import Engine, text

logger = logging.getLogger("cobranzas.persistencia")

ALTERS = [
    "ALTER TABLE deudores ADD COLUMN socio VARCHAR(20)",
    "ALTER TABLE deuda ADD COLUMN fecha_corte DATE",
    "ALTER TABLE deuda ADD COLUMN archivo_origen VARCHAR(500)",
    "ALTER TABLE deuda ADD COLUMN fecha_carga DATETIME",
    "ALTER TABLE deuda ADD COLUMN desc_oficina VARCHAR(200)",
    "ALTER TABLE deuda ADD COLUMN socio VARCHAR(50)",
    "ALTER TABLE deuda ADD COLUMN nombre VARCHAR(300)",
    "ALTER TABLE deuda ADD COLUMN cedula VARCHAR(30)",
    "ALTER TABLE deuda ADD COLUMN oficina VARCHAR(50)",
    "ALTER TABLE deuda ADD COLUMN sector VARCHAR(100)",
    "ALTER TABLE deuda ADD COLUMN tipo_operacion VARCHAR(100)",
    "ALTER TABLE deuda ADD COLUMN tipo_destino VARCHAR(100)",
    "ALTER TABLE deuda ADD COLUMN valor_original_prestamo NUMERIC(18, 2)",
    "ALTER TABLE deuda ADD COLUMN saldo_capital_prestamo NUMERIC(18, 2)",
    "ALTER TABLE deuda ADD COLUMN calificacion VARCHAR(20)",
    "ALTER TABLE deuda ADD COLUMN total_provision NUMERIC(18, 2)",
    "ALTER TABLE deuda ADD COLUMN saldo_140x NUMERIC(18, 2)",
    "ALTER TABLE deuda ADD COLUMN saldo_141x NUMERIC(18, 2)",
    "ALTER TABLE deuda ADD COLUMN saldo_142x NUMERIC(18, 2)",
    "ALTER TABLE deuda ADD COLUMN interes_normal NUMERIC(18, 2)",
    "ALTER TABLE deuda ADD COLUMN interes_devengado NUMERIC(18, 2)",
    "ALTER TABLE deuda ADD COLUMN interes_vencido NUMERIC(18, 2)",
    "ALTER TABLE deuda ADD COLUMN interes_resolucion NUMERIC(18, 2)",
    "ALTER TABLE deuda ADD COLUMN interes_castigado NUMERIC(18, 2)",
    "ALTER TABLE deuda ADD COLUMN interes_mora NUMERIC(18, 2)",
    "ALTER TABLE deuda ADD COLUMN otros_rubros_deuda NUMERIC(18, 2)",
    "ALTER TABLE deuda ADD COLUMN total_operacion NUMERIC(38, 10)",
    "ALTER TABLE deuda ADD COLUMN estado VARCHAR(100)",
    "ALTER TABLE deuda ADD COLUMN oficial VARCHAR(200)",
    "ALTER TABLE deuda ADD COLUMN dias_mora INTEGER",
    "ALTER TABLE deuda ADD COLUMN dias_atraso_camorosico INTEGER",
    "ALTER TABLE deuda ADD COLUMN fecha_ingreso DATE",
    "ALTER TABLE deuda ADD COLUMN tipo VARCHAR(50)",
    "ALTER TABLE deuda ADD COLUMN dia_pago INTEGER",
    "ALTER TABLE deuda ADD COLUMN valor_cuota NUMERIC(18, 2)",
    "ALTER TABLE deuda ADD COLUMN cuota_actual INTEGER",
    "ALTER TABLE deuda ADD COLUMN dividendos INTEGER",
    "ALTER TABLE deuda ADD COLUMN cod_oficial_asignado VARCHAR(50)",
    "ALTER TABLE deuda ADD COLUMN oficial_asignado VARCHAR(200)",
    "ALTER TABLE deuda ADD COLUMN cod_oficial_adm VARCHAR(50)",
    "ALTER TABLE deuda ADD COLUMN oficial_adm VARCHAR(200)",
    "ALTER TABLE deuda ADD COLUMN operacion_homologada VARCHAR(50)",
    "ALTER TABLE deuda ADD COLUMN decision VARCHAR(100)",
    "ALTER TABLE deuda ADD COLUMN segmentacion VARCHAR(100)",
    "ALTER TABLE deuda ADD COLUMN score VARCHAR(100)",
    "ALTER TABLE deuda ADD COLUMN fuente_repago VARCHAR(200)",
    "ALTER TABLE deuda ADD COLUMN identificacion_ifi VARCHAR(100)",
    "ALTER TABLE deuda ADD COLUMN actividad_economica VARCHAR(500)",
    "ALTER TABLE deuda ADD COLUMN fecha_archivo DATE",
    "ALTER TABLE deuda ADD COLUMN tipo_mes VARCHAR(2)",
    "ALTER TABLE deuda ADD COLUMN tipo_fideicomiso VARCHAR(2)",
    "ALTER TABLE deuda ADD COLUMN proceso_cod INTEGER",
    "ALTER TABLE asesores_deuda ADD COLUMN id_credito_recblue VARCHAR(100)",
]

COPIAS = [
    """
    UPDATE deuda SET desc_oficina = descripcion_oficina
    WHERE desc_oficina IS NULL AND descripcion_oficina IS NOT NULL
    """
]


def migrar_sqlite_si_aplica(engine: Engine) -> int:
    """Aplica ALTER TABLE pendientes. Retorna cantidad de columnas nuevas."""
    if engine.dialect.name != "sqlite":
        return 0

    aplicadas = 0
    with engine.begin() as conn:
        for sql in ALTERS:
            try:
                conn.execute(text(sql))
                aplicadas += 1
                logger.info("SQLite migración: %s", sql)
            except Exception as exc:
                if "duplicate column" in str(exc).lower():
                    continue
                raise
        for sql in COPIAS:
            try:
                conn.execute(text(sql))
            except Exception as exc:
                if "no such column" in str(exc).lower():
                    continue
                raise
    return aplicadas
