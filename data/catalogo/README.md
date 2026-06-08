# Catálogo (Excel)

## Asesores — Job 0

**`asesores.xlsx`** (`ARCHIVO_EXCEL_ASESORES`)

Columnas: `cedula`, `nombre`, `numero_telefono`, `email`, `activo`.

```powershell
python main.py plantilla
```

## Feriados — Job 0b

**`dias_feriados.xlsx`** (`EXCEL_DIR` + `EXCEL_PATTERN`)

Filas: descripción + fecha (M/D/Y) o rango con fecha inicio y fin.

```powershell
python main.py plantilla-feriados
```

## Notificaciones de errores

**`notificaciones_errores.xlsx`** (`ARCHIVO_EXCEL_NOTIFICACIONES`)

Columnas: `nombre`, `email`, `activo` (`si`/`no`).

Se usa cuando `NOTIFICACIONES_ERRORES_HABILITADO=true` y falla el pipeline.

```powershell
python main.py plantilla-notificaciones
```
