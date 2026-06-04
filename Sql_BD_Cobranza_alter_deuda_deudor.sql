-- Migración: ampliar deudores y deuda (SQL Server)
-- Ejecutar en BD_Cobranza si la base ya existía con el esquema anterior.

ALTER TABLE deudores ADD socio NVARCHAR(20) NULL;
GO

ALTER TABLE deuda ADD oficina NVARCHAR(20) NULL;
ALTER TABLE deuda ADD descripcion_oficina NVARCHAR(100) NULL;
ALTER TABLE deuda ADD sector NVARCHAR(10) NULL;
ALTER TABLE deuda ADD tipo_operacion NVARCHAR(50) NULL;
ALTER TABLE deuda ADD tipo_destino NVARCHAR(20) NULL;
ALTER TABLE deuda ADD valor_original_prestamo NUMERIC(18, 2) NULL;
ALTER TABLE deuda ADD saldo_capital_prestamo NUMERIC(18, 2) NULL;
ALTER TABLE deuda ADD calificacion NVARCHAR(10) NULL;
ALTER TABLE deuda ADD total_provision NUMERIC(18, 2) NULL;
ALTER TABLE deuda ADD saldo NUMERIC(18, 2) NULL;
GO
