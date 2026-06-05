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
    fecha_corte DATE,
    archivo_origen VARCHAR(500),
    fecha_carga DATETIME,
    oficina VARCHAR(50),
    desc_oficina VARCHAR(200),
    socio VARCHAR(50),
    nombre VARCHAR(300),
    cedula VARCHAR(30),
    sector VARCHAR(100),
    tipo_operacion VARCHAR(100),
    tipo_destino VARCHAR(100),
    fecha_concesion DATE,
    fecha_vencimiento DATE,
    fecha_ultimo_pago DATE,
    valor_original_prestamo NUMERIC(18, 2),
    saldo_capital_prestamo NUMERIC(18, 2),
    calificacion VARCHAR(20),
    total_provision NUMERIC(18, 2),
    saldo_140x NUMERIC(18, 2),
    saldo_141x NUMERIC(18, 2),
    saldo_142x NUMERIC(18, 2),
    interes_normal NUMERIC(18, 2),
    interes_devengado NUMERIC(18, 2),
    interes_vencido NUMERIC(18, 2),
    interes_resolucion NUMERIC(18, 2),
    interes_castigado NUMERIC(18, 2),
    interes_mora NUMERIC(18, 2),
    otros_rubros_deuda NUMERIC(18, 2),
    total_operacion NUMERIC(38, 10),
    estado VARCHAR(100),
    oficial VARCHAR(200),
    dias_mora INTEGER,
    fecha_ingreso DATE,
    tipo VARCHAR(50),
    dia_pago INTEGER,
    valor_cuota NUMERIC(18, 2),
    cuota_actual INTEGER,
    dividendos INTEGER,
    cod_oficial_asignado VARCHAR(50),
    oficial_asignado VARCHAR(200),
    cod_oficial_adm VARCHAR(50),
    oficial_adm VARCHAR(200),
    operacion_homologada VARCHAR(50),
    decision VARCHAR(100),
    segmentacion VARCHAR(100),
    score VARCHAR(100),
    fuente_repago VARCHAR(200),
    identificacion_ifi VARCHAR(100),
    actividad_economica VARCHAR(500),
    fecha_archivo DATE,
    tipo_mes VARCHAR(2),
    tipo_fideicomiso VARCHAR(2),
    proceso_cod INTEGER,
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
