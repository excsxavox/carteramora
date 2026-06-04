USE [master]
GO
/****** Object:  Database [BD_Cobranza]    Script Date: 6/4/2026 1:08:46 PM ******/
CREATE DATABASE [BD_Cobranza]
 CONTAINMENT = NONE
 ON  PRIMARY 
( NAME = N'BD_Cobranza', FILENAME = N'C:\Program Files\Microsoft SQL Server\MSSQL17.SQLEXPRESS\MSSQL\DATA\BD_Cobranza.mdf' , SIZE = 8192KB , MAXSIZE = UNLIMITED, FILEGROWTH = 65536KB )
 LOG ON 
( NAME = N'BD_Cobranza_log', FILENAME = N'C:\Program Files\Microsoft SQL Server\MSSQL17.SQLEXPRESS\MSSQL\DATA\BD_Cobranza_log.ldf' , SIZE = 8192KB , MAXSIZE = 2048GB , FILEGROWTH = 65536KB )
 WITH CATALOG_COLLATION = DATABASE_DEFAULT, LEDGER = OFF
GO
ALTER DATABASE [BD_Cobranza] SET COMPATIBILITY_LEVEL = 170
GO
IF (1 = FULLTEXTSERVICEPROPERTY('IsFullTextInstalled'))
begin
EXEC [BD_Cobranza].[dbo].[sp_fulltext_database] @action = 'enable'
end
GO
ALTER DATABASE [BD_Cobranza] SET ANSI_NULL_DEFAULT OFF 
GO
ALTER DATABASE [BD_Cobranza] SET ANSI_NULLS OFF 
GO
ALTER DATABASE [BD_Cobranza] SET ANSI_PADDING OFF 
GO
ALTER DATABASE [BD_Cobranza] SET ANSI_WARNINGS OFF 
GO
ALTER DATABASE [BD_Cobranza] SET ARITHABORT OFF 
GO
ALTER DATABASE [BD_Cobranza] SET AUTO_CLOSE OFF 
GO
ALTER DATABASE [BD_Cobranza] SET AUTO_SHRINK OFF 
GO
ALTER DATABASE [BD_Cobranza] SET AUTO_UPDATE_STATISTICS ON 
GO
ALTER DATABASE [BD_Cobranza] SET CURSOR_CLOSE_ON_COMMIT OFF 
GO
ALTER DATABASE [BD_Cobranza] SET CURSOR_DEFAULT  GLOBAL 
GO
ALTER DATABASE [BD_Cobranza] SET CONCAT_NULL_YIELDS_NULL OFF 
GO
ALTER DATABASE [BD_Cobranza] SET NUMERIC_ROUNDABORT OFF 
GO
ALTER DATABASE [BD_Cobranza] SET QUOTED_IDENTIFIER OFF 
GO
ALTER DATABASE [BD_Cobranza] SET RECURSIVE_TRIGGERS OFF 
GO
ALTER DATABASE [BD_Cobranza] SET  DISABLE_BROKER 
GO
ALTER DATABASE [BD_Cobranza] SET AUTO_UPDATE_STATISTICS_ASYNC OFF 
GO
ALTER DATABASE [BD_Cobranza] SET DATE_CORRELATION_OPTIMIZATION OFF 
GO
ALTER DATABASE [BD_Cobranza] SET TRUSTWORTHY OFF 
GO
ALTER DATABASE [BD_Cobranza] SET ALLOW_SNAPSHOT_ISOLATION OFF 
GO
ALTER DATABASE [BD_Cobranza] SET PARAMETERIZATION SIMPLE 
GO
ALTER DATABASE [BD_Cobranza] SET READ_COMMITTED_SNAPSHOT OFF 
GO
ALTER DATABASE [BD_Cobranza] SET HONOR_BROKER_PRIORITY OFF 
GO
ALTER DATABASE [BD_Cobranza] SET RECOVERY SIMPLE 
GO
ALTER DATABASE [BD_Cobranza] SET  MULTI_USER 
GO
ALTER DATABASE [BD_Cobranza] SET PAGE_VERIFY CHECKSUM  
GO
ALTER DATABASE [BD_Cobranza] SET DB_CHAINING OFF 
GO
ALTER DATABASE [BD_Cobranza] SET FILESTREAM( NON_TRANSACTED_ACCESS = OFF ) 
GO
ALTER DATABASE [BD_Cobranza] SET TARGET_RECOVERY_TIME = 60 SECONDS 
GO
ALTER DATABASE [BD_Cobranza] SET DELAYED_DURABILITY = DISABLED 
GO
ALTER DATABASE [BD_Cobranza] SET OPTIMIZED_LOCKING = OFF 
GO
ALTER DATABASE [BD_Cobranza] SET ACCELERATED_DATABASE_RECOVERY = OFF  
GO
ALTER DATABASE [BD_Cobranza] SET QUERY_STORE = ON
GO
ALTER DATABASE [BD_Cobranza] SET QUERY_STORE (OPERATION_MODE = READ_WRITE, CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = 30), DATA_FLUSH_INTERVAL_SECONDS = 900, INTERVAL_LENGTH_MINUTES = 60, MAX_STORAGE_SIZE_MB = 1000, QUERY_CAPTURE_MODE = AUTO, SIZE_BASED_CLEANUP_MODE = AUTO, MAX_PLANS_PER_QUERY = 200, WAIT_STATS_CAPTURE_MODE = ON)
GO
USE [BD_Cobranza]
GO
/****** Object:  Table [dbo].[asesores]    Script Date: 6/4/2026 1:08:46 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[asesores](
	[id_asesor] [int] IDENTITY(1,1) NOT NULL,
	[nombre] [nvarchar](150) NULL,
	[cedula] [nvarchar](20) NULL,
	[numero_telefono] [nvarchar](20) NULL,
	[email] [nvarchar](150) NULL,
	[activo] [bit] NULL,
	[creado_en] [datetime2](7) NULL,
PRIMARY KEY CLUSTERED 
(
	[id_asesor] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[cedula] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[asesores_deuda]    Script Date: 6/4/2026 1:08:46 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[asesores_deuda](
	[id_asesor_deuda] [int] IDENTITY(1,1) NOT NULL,
	[id_catalogo] [int] NOT NULL,
	[id_asesor] [int] NOT NULL,
	[id_deuda] [int] NOT NULL,
	[estado] [nvarchar](50) NULL,
	[monto] [decimal](18, 2) NULL,
	[monto_inicial] [decimal](18, 2) NULL,
	[monto_mora] [decimal](18, 2) NULL,
	[fecha_asignacion] [date] NULL,
	[fecha_modificacion] [datetime2](7) NULL,
PRIMARY KEY CLUSTERED 
(
	[id_asesor_deuda] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[catalogo]    Script Date: 6/4/2026 1:08:46 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[catalogo](
	[id_catalogo] [int] IDENTITY(1,1) NOT NULL,
	[id_clave] [int] NOT NULL,
	[valor] [nvarchar](200) NULL,
	[descripcion] [nvarchar](250) NULL,
	[fecha_creacion] [datetime2](7) NULL,
	[vigencia] [bit] NULL,
	[fecha_modificacion] [datetime2](7) NULL,
PRIMARY KEY CLUSTERED 
(
	[id_catalogo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[claves]    Script Date: 6/4/2026 1:08:46 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[claves](
	[id_clave] [int] IDENTITY(1,1) NOT NULL,
	[clave] [varchar](20) NULL,
	[descripcion] [varchar](250) NULL,
	[fecha_creacion] [datetime2](7) NULL,
	[vigente] [bit] NULL,
	[fecha_modificacion] [datetime2](7) NULL,
PRIMARY KEY CLUSTERED 
(
	[id_clave] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[deuda]    Script Date: 6/4/2026 1:08:46 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[deuda](
	[id_deuda] [int] IDENTITY(1,1) NOT NULL,
	[id_deudor] [int] NOT NULL,
	[numero_operacion] [nvarchar](50) NULL,
	[oficina] [nvarchar](20) NULL,
	[descripcion_oficina] [nvarchar](100) NULL,
	[sector] [nvarchar](10) NULL,
	[tipo_operacion] [nvarchar](50) NULL,
	[tipo_destino] [nvarchar](20) NULL,
	[fecha_concesion] [date] NULL,
	[fecha_vencimiento] [date] NULL,
	[fecha_ultimo_pago] [date] NULL,
	[valor_original_prestamo] [numeric](18, 2) NULL,
	[saldo_capital_prestamo] [numeric](18, 2) NULL,
	[calificacion] [nvarchar](10) NULL,
	[total_provision] [numeric](18, 2) NULL,
	[saldo] [numeric](18, 2) NULL,
	[fecha_pago] [date] NULL,
	[creado_en] [datetime2](7) NULL,
PRIMARY KEY CLUSTERED 
(
	[id_deuda] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[numero_operacion] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[deudores]    Script Date: 6/4/2026 1:08:46 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[deudores](
	[id_deudor] [int] IDENTITY(1,1) NOT NULL,
	[nombre] [nvarchar](150) NULL,
	[documento] [nvarchar](20) NULL,
	[socio] [nvarchar](20) NULL,
	[creado_en] [datetime2](7) NULL,
PRIMARY KEY CLUSTERED 
(
	[id_deudor] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[logs_auditoria]    Script Date: 6/4/2026 1:08:46 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[logs_auditoria](
	[id_log] [int] IDENTITY(1,1) NOT NULL,
	[tabla] [nvarchar](100) NULL,
	[operacion] [nvarchar](50) NULL,
	[usuario] [nvarchar](100) NULL,
	[datos_anteriores] [nvarchar](max) NULL,
	[datos_nuevos] [nvarchar](max) NULL,
	[registrado_en] [datetime2](7) NULL,
PRIMARY KEY CLUSTERED 
(
	[id_log] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[reglas]    Script Date: 6/4/2026 1:08:46 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[reglas](
	[id_regla] [int] IDENTITY(1,1) NOT NULL,
	[nombre] [nvarchar](150) NULL,
	[descripcion] [nvarchar](500) NULL,
	[tipo] [nvarchar](100) NULL,
	[valor] [nvarchar](max) NULL,
	[prioridad] [int] NULL,
	[activo] [bit] NULL,
	[creado_en] [datetime2](7) NULL,
	[fecha_modificacion] [datetime2](7) NULL,
PRIMARY KEY CLUSTERED 
(
	[id_regla] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
ALTER TABLE [dbo].[asesores] ADD  DEFAULT ((1)) FOR [activo]
GO
ALTER TABLE [dbo].[asesores] ADD  DEFAULT (sysutcdatetime()) FOR [creado_en]
GO
ALTER TABLE [dbo].[reglas] ADD  DEFAULT ((0)) FOR [prioridad]
GO
ALTER TABLE [dbo].[reglas] ADD  DEFAULT ((1)) FOR [activo]
GO
ALTER TABLE [dbo].[asesores_deuda]  WITH CHECK ADD  CONSTRAINT [fk_ad_asesores] FOREIGN KEY([id_asesor])
REFERENCES [dbo].[asesores] ([id_asesor])
GO
ALTER TABLE [dbo].[asesores_deuda] CHECK CONSTRAINT [fk_ad_asesores]
GO
ALTER TABLE [dbo].[asesores_deuda]  WITH CHECK ADD  CONSTRAINT [fk_ad_deuda] FOREIGN KEY([id_deuda])
REFERENCES [dbo].[deuda] ([id_deuda])
GO
ALTER TABLE [dbo].[asesores_deuda] CHECK CONSTRAINT [fk_ad_deuda]
GO
ALTER TABLE [dbo].[catalogo]  WITH CHECK ADD  CONSTRAINT [fk_catalogo_claves] FOREIGN KEY([id_clave])
REFERENCES [dbo].[claves] ([id_clave])
GO
ALTER TABLE [dbo].[catalogo] CHECK CONSTRAINT [fk_catalogo_claves]
GO
ALTER TABLE [dbo].[deuda]  WITH CHECK ADD  CONSTRAINT [fk_deuda_deudores] FOREIGN KEY([id_deudor])
REFERENCES [dbo].[deudores] ([id_deudor])
GO
ALTER TABLE [dbo].[deuda] CHECK CONSTRAINT [fk_deuda_deudores]
GO
USE [master]
GO
ALTER DATABASE [BD_Cobranza] SET  READ_WRITE 
GO
