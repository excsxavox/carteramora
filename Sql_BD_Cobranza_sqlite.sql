-- Esquema BD_Cobranza para SQLite (referencia; el job usa SQLAlchemy create_all)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS asesores (
    id_asesor INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(150),
    cedula VARCHAR(20) UNIQUE,
    numero_telefono VARCHAR(20),
    email VARCHAR(150),
    activo BOOLEAN DEFAULT 1,
    creado_en DATETIME
);

CREATE TABLE IF NOT EXISTS deudores (
    id_deudor INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(150),
    documento VARCHAR(20),
    socio VARCHAR(20),
    creado_en DATETIME
);

CREATE TABLE IF NOT EXISTS deuda (
    id_deuda INTEGER PRIMARY KEY AUTOINCREMENT,
    id_deudor INTEGER NOT NULL,
    numero_operacion VARCHAR(50) UNIQUE,
    oficina VARCHAR(20),
    descripcion_oficina VARCHAR(100),
    sector VARCHAR(10),
    tipo_operacion VARCHAR(50),
    tipo_destino VARCHAR(20),
    fecha_concesion DATE,
    fecha_vencimiento DATE,
    fecha_ultimo_pago DATE,
    valor_original_prestamo NUMERIC(18, 2),
    saldo_capital_prestamo NUMERIC(18, 2),
    calificacion VARCHAR(10),
    total_provision NUMERIC(18, 2),
    saldo NUMERIC(18, 2),
    fecha_pago DATE,
    creado_en DATETIME,
    FOREIGN KEY (id_deudor) REFERENCES deudores (id_deudor)
);

CREATE TABLE IF NOT EXISTS claves (
    id_clave INTEGER PRIMARY KEY AUTOINCREMENT,
    clave VARCHAR(20),
    descripcion VARCHAR(250),
    fecha_creacion DATETIME,
    vigente BOOLEAN,
    fecha_modificacion DATETIME
);

CREATE TABLE IF NOT EXISTS catalogo (
    id_catalogo INTEGER PRIMARY KEY AUTOINCREMENT,
    id_clave INTEGER NOT NULL,
    valor VARCHAR(200),
    descripcion VARCHAR(250),
    fecha_creacion DATETIME,
    vigencia BOOLEAN,
    fecha_modificacion DATETIME,
    FOREIGN KEY (id_clave) REFERENCES claves (id_clave)
);

CREATE TABLE IF NOT EXISTS asesores_deuda (
    id_asesor_deuda INTEGER PRIMARY KEY AUTOINCREMENT,
    id_catalogo INTEGER NOT NULL,
    id_asesor INTEGER NOT NULL,
    id_deuda INTEGER NOT NULL,
    estado VARCHAR(50),
    monto NUMERIC(18, 2),
    monto_inicial NUMERIC(18, 2),
    monto_mora NUMERIC(18, 2),
    fecha_asignacion DATE,
    fecha_modificacion DATETIME,
    FOREIGN KEY (id_asesor) REFERENCES asesores (id_asesor),
    FOREIGN KEY (id_deuda) REFERENCES deuda (id_deuda)
);

CREATE TABLE IF NOT EXISTS reglas (
    id_regla INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(150),
    descripcion VARCHAR(500),
    tipo VARCHAR(100),
    valor TEXT,
    prioridad INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT 1,
    creado_en DATETIME,
    fecha_modificacion DATETIME
);

CREATE TABLE IF NOT EXISTS logs_auditoria (
    id_log INTEGER PRIMARY KEY AUTOINCREMENT,
    tabla VARCHAR(100),
    operacion VARCHAR(50),
    usuario VARCHAR(100),
    datos_anteriores TEXT,
    datos_nuevos TEXT,
    registrado_en DATETIME
);
