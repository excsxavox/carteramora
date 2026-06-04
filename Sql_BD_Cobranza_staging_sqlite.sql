-- Tablas temporales (Job 2: carga desde .lis limpios)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS tmp_lote_carga (
    id_lote INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_carga DATETIME NOT NULL,
    ruta_archivo_morosidad VARCHAR(500) NOT NULL,
    ruta_archivo_mora VARCHAR(500) NOT NULL,
    estado VARCHAR(30) NOT NULL DEFAULT 'cargado',
    filas_morosidad INTEGER NOT NULL DEFAULT 0,
    filas_mora INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS tmp_columna_archivo (
    id_columna INTEGER PRIMARY KEY AUTOINCREMENT,
    id_lote INTEGER NOT NULL,
    tipo_archivo VARCHAR(20) NOT NULL,
    orden INTEGER NOT NULL,
    nombre_columna VARCHAR(120) NOT NULL,
    nombre_original VARCHAR(250) NOT NULL,
    FOREIGN KEY (id_lote) REFERENCES tmp_lote_carga (id_lote)
);

CREATE TABLE IF NOT EXISTS tmp_stg_morosidad (
    id_fila INTEGER PRIMARY KEY AUTOINCREMENT,
    id_lote INTEGER NOT NULL,
    numero_fila INTEGER NOT NULL,
    no_operacion VARCHAR(50),
    campos_json TEXT NOT NULL,
    FOREIGN KEY (id_lote) REFERENCES tmp_lote_carga (id_lote)
);
CREATE INDEX IF NOT EXISTS ix_tmp_stg_morosidad_lote ON tmp_stg_morosidad (id_lote);
CREATE INDEX IF NOT EXISTS ix_tmp_stg_morosidad_oper ON tmp_stg_morosidad (no_operacion);

CREATE TABLE IF NOT EXISTS tmp_stg_mora (
    id_fila INTEGER PRIMARY KEY AUTOINCREMENT,
    id_lote INTEGER NOT NULL,
    numero_fila INTEGER NOT NULL,
    no_operacion VARCHAR(50),
    campos_json TEXT NOT NULL,
    FOREIGN KEY (id_lote) REFERENCES tmp_lote_carga (id_lote)
);
CREATE INDEX IF NOT EXISTS ix_tmp_stg_mora_lote ON tmp_stg_mora (id_lote);
CREATE INDEX IF NOT EXISTS ix_tmp_stg_mora_oper ON tmp_stg_mora (no_operacion);

CREATE TABLE IF NOT EXISTS tmp_mapeo_columna (
    id_mapeo INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_archivo VARCHAR(20) NOT NULL,
    columna_origen VARCHAR(120) NOT NULL,
    tabla_destino VARCHAR(80) NOT NULL,
    columna_destino VARCHAR(120) NOT NULL,
    activo BOOLEAN DEFAULT 1,
    fecha_creacion DATETIME
);
