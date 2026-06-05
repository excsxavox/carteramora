# docsmora — Carpetas de ejecución

Estructura por **año / fecha de corte / lote**:

```
docsmora/
└── 2026/
    └── 05042026/              # Fecha de corte (DDMMYYYY)
        └── cartera05042026b/  # Lote de cartera
            ├── camorosico_06032026_0047_of_0.lis      (cuadro morosidad)
            └── cadetacaco_cie06032026_0233_of_0.lis   (reporte detallado cartera)
```

## Ejecutar (rutas automáticas)

En `.env` solo necesitas:

```env
DOCSMORA_DIR=docsmora
DESTINO_DIR=destino
USAR_RUTAS_AUTOMATICAS=true
```

El job busca **la fecha de hoy** (`DDMMYYYY`, ej. `05062026`):

```
docsmora/2026/05062026/cartera05062026b/
  camorosico_05062026_....lis
  cadetacaco_cie05062026_....lis
```

Salidas en `destino/2026/05062026/cartera05062026b/`.

Para otra fecha: `FECHA_CORTE=05042026`

```bash
python main.py
```

Coloca aquí los archivos exportados del core (TAB) antes de cada corrida.
