-- Migración: ampliar deudores y deuda (SQL Server)
-- Ejecutar en BD_Cobranza si la base ya existía con el esquema anterior.

IF COL_LENGTH('deudores', 'socio') IS NULL
    ALTER TABLE deudores ADD socio NVARCHAR(20) NULL;
GO

-- Columnas nuevas en deuda (omitir las que ya existan)
DECLARE @cols TABLE (sql NVARCHAR(500));
INSERT INTO @cols (sql) VALUES
('ALTER TABLE deuda ADD fecha_corte DATE NULL'),
('ALTER TABLE deuda ADD archivo_origen VARCHAR(500) NULL'),
('ALTER TABLE deuda ADD fecha_carga DATETIME2(7) NULL'),
('ALTER TABLE deuda ADD desc_oficina VARCHAR(200) NULL'),
('ALTER TABLE deuda ADD socio VARCHAR(50) NULL'),
('ALTER TABLE deuda ADD nombre VARCHAR(300) NULL'),
('ALTER TABLE deuda ADD cedula VARCHAR(30) NULL'),
('ALTER TABLE deuda ADD saldo_140x DECIMAL(18, 2) NULL'),
('ALTER TABLE deuda ADD saldo_141x DECIMAL(18, 2) NULL'),
('ALTER TABLE deuda ADD saldo_142x DECIMAL(18, 2) NULL'),
('ALTER TABLE deuda ADD interes_normal DECIMAL(18, 2) NULL'),
('ALTER TABLE deuda ADD interes_devengado DECIMAL(18, 2) NULL'),
('ALTER TABLE deuda ADD interes_vencido DECIMAL(18, 2) NULL'),
('ALTER TABLE deuda ADD interes_resolucion DECIMAL(18, 2) NULL'),
('ALTER TABLE deuda ADD interes_castigado DECIMAL(18, 2) NULL'),
('ALTER TABLE deuda ADD interes_mora DECIMAL(18, 2) NULL'),
('ALTER TABLE deuda ADD otros_rubros_deuda DECIMAL(18, 2) NULL'),
('ALTER TABLE deuda ADD total_operacion DECIMAL(38, 10) NULL'),
('ALTER TABLE deuda ADD estado VARCHAR(100) NULL'),
('ALTER TABLE deuda ADD oficial VARCHAR(200) NULL'),
('ALTER TABLE deuda ADD dias_mora INT NULL'),
('ALTER TABLE deuda ADD dias_atraso_camorosico INT NULL'),
('ALTER TABLE deuda ADD fecha_ingreso DATE NULL'),
('ALTER TABLE deuda ADD tipo VARCHAR(50) NULL'),
('ALTER TABLE deuda ADD dia_pago INT NULL'),
('ALTER TABLE deuda ADD valor_cuota DECIMAL(18, 2) NULL'),
('ALTER TABLE deuda ADD cuota_actual INT NULL'),
('ALTER TABLE deuda ADD dividendos INT NULL'),
('ALTER TABLE deuda ADD cod_oficial_asignado VARCHAR(50) NULL'),
('ALTER TABLE deuda ADD oficial_asignado VARCHAR(200) NULL'),
('ALTER TABLE deuda ADD cod_oficial_adm VARCHAR(50) NULL'),
('ALTER TABLE deuda ADD oficial_adm VARCHAR(200) NULL'),
('ALTER TABLE deuda ADD operacion_homologada VARCHAR(50) NULL'),
('ALTER TABLE deuda ADD decision VARCHAR(100) NULL'),
('ALTER TABLE deuda ADD segmentacion VARCHAR(100) NULL'),
('ALTER TABLE deuda ADD score VARCHAR(100) NULL'),
('ALTER TABLE deuda ADD fuente_repago VARCHAR(200) NULL'),
('ALTER TABLE deuda ADD identificacion_ifi VARCHAR(100) NULL'),
('ALTER TABLE deuda ADD actividad_economica VARCHAR(500) NULL'),
('ALTER TABLE deuda ADD fecha_archivo DATE NULL'),
('ALTER TABLE deuda ADD tipo_mes VARCHAR(2) NULL'),
('ALTER TABLE deuda ADD tipo_fideicomiso VARCHAR(2) NULL'),
('ALTER TABLE deuda ADD proceso_cod BIGINT NULL');

DECLARE @s NVARCHAR(500);
DECLARE c CURSOR FOR SELECT sql FROM @cols;
OPEN c;
FETCH NEXT FROM c INTO @s;
WHILE @@FETCH_STATUS = 0
BEGIN
    BEGIN TRY
        EXEC sp_executesql @s;
    END TRY
    BEGIN CATCH
        IF ERROR_NUMBER() NOT IN (2705, 1911) THROW;
    END CATCH
    FETCH NEXT FROM c INTO @s;
END
CLOSE c;
DEALLOCATE c;
GO

-- Copiar descripcion_oficina → desc_oficina si aplica
IF COL_LENGTH('deuda', 'descripcion_oficina') IS NOT NULL
   AND COL_LENGTH('deuda', 'desc_oficina') IS NOT NULL
    UPDATE deuda SET desc_oficina = descripcion_oficina
    WHERE desc_oficina IS NULL AND descripcion_oficina IS NOT NULL;
GO
