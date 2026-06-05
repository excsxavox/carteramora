# Cobranzas — Cartera en mora

Jobs en Python (hexagonal + cadena de responsabilidad) para procesar cartera en mora desde archivos `.lis` del core.

## Estructura del proyecto

```
cartera mora/
├── main.py                 # Único comando de entrada
├── .env                    # Configuración (no subir a git)
├── data/catalogo/          # Excel de asesores (asesores.xlsx)
├── docsmora/               # Entradas del core (.lis)
├── destino/                # Salidas limpias (.lis)
├── data/BD_Cobranza.sqlite # Base SQLite (generada)
├── src/cobranzas/          # Código fuente
├── tests/
├── docs/                   # Documentación técnica
└── Sql_BD_Cobranza*.sql    # DDL referencia
```

## Comandos

```powershell
.venv\Scripts\activate
pip install -e .
```

| Comando | Descripción |
|---------|-------------|
| `python main.py` | **Todo el flujo diario** (asesores → feriados → limpieza → BD → ASIGNACION.csv) |
| `python main.py sync` | Solo sincronizar asesores desde Excel |
| `python main.py sync-feriados` | Solo sincronizar feriados desde Excel |
| `python main.py limpieza` | Solo limpieza → `detalle_morosidad.lis` + `reporte_mora.lis` |
| `python main.py staging` | Cargar `.lis` limpios a tablas `tmp_*` |
| `python main.py init-db` | Crear tablas SQLite |
| `python main.py plantilla` | Crear `data/catalogo/asesores.xlsx` |

## Primera vez

```powershell
python main.py plantilla
# Colocar dias_feriados.xlsx en data/catalogo y asesores.xlsx
python main.py
```

## Flujo de jobs

```
asesores.xlsx     →  [sync]         →  tabla asesores
*feriados*.xlsx   →  [sync-feriados] →  claves + catalogo (feriados_catalogo)
docsmora/*.lis    →  [limpieza]     →  destino/*.lis + ASIGNACION.csv + BD
destino/*.lis     →  [staging]      →  tmp_stg_*
```

## Configuración (`.env`)

Ver `.env.example`. Principales variables:

- `ARCHIVO_EXCEL_ASESORES` — Excel de asesores
- `DIRECTORIO_EXCEL_FERIADOS` / `PATRON_EXCEL_FERIADOS` / `CLAVE_FERIADOS` — catálogo de feriados
- `USAR_MORA_TEMPRANA`, `MORA_TEMPRANA_DIAS_MIN/MAX`, `ESTADOS_EXCLUIDOS`, `TIPOS_OPER_EXCLUIDOS` — HU-GRC-01
- `ARCHIVO_SALIDA_ASIGNACION`, `ARCHIVO_RECBLUE` — asignación y Recblue (asesores desde BD / Job 0)
- `ARCHIVO_MOROSIDAD` / `ARCHIVO_CARTERA` — entradas core
- `ARCHIVO_SALIDA_MOROSIDAD` / `ARCHIVO_SALIDA_MORA` — salidas
- `DATABASE_URL`, `PERSISTIR_EN_BD`, `SYNC_ASESORES_RECHAZAR_DUPLICADOS`

## Tests

```powershell
pytest
```

Más detalle: `docs/BD_Cobranza_ORM.md` · Diagrama ER: `docs/BD_Cobranza.mmd`
