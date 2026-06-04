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
| `python main.py` | **Pipeline:** Excel asesores + limpieza (uso diario) |
| `python main.py sync` | Solo sincronizar asesores desde Excel |
| `python main.py limpieza` | Solo limpieza → `detalle_morosidad.lis` + `reporte_mora.lis` |
| `python main.py staging` | Cargar `.lis` limpios a tablas `tmp_*` |
| `python main.py init-db` | Crear tablas SQLite |
| `python main.py plantilla` | Crear `data/catalogo/asesores.xlsx` |

## Primera vez

```powershell
python main.py init-db
python main.py plantilla
# Editar data/catalogo/asesores.xlsx con tu catálogo real
python main.py
```

## Flujo de jobs

```
data/catalogo/asesores.xlsx  →  [sync]  →  tabla asesores
docsmora/*.lis               →  [limpieza]  →  destino/*.lis
destino/*.lis                →  [staging]  →  tmp_stg_*
```

## Configuración (`.env`)

Ver `.env.example`. Principales variables:

- `ARCHIVO_EXCEL_ASESORES` — Excel de asesores
- `ARCHIVO_MOROSIDAD` / `ARCHIVO_CARTERA` — entradas core
- `ARCHIVO_SALIDA_MOROSIDAD` / `ARCHIVO_SALIDA_MORA` — salidas
- `DATABASE_URL`, `PERSISTIR_EN_BD`, `SYNC_ASESORES_RECHAZAR_DUPLICADOS`

## Tests

```powershell
pytest
```

Más detalle: `docs/BD_Cobranza_ORM.md` · Diagrama ER: `docs/BD_Cobranza.mmd`
